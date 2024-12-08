import logging
from src.models.claim import Claim
from src.models.revert import Revert
from src.models.pharmacy import Pharmacy
from .analytics_interface import AnalyticsInterface
from typing import List
import json


class Analytics(AnalyticsInterface):
    def __init__(self) -> None:
        pass

    def __process_claims_and_reverts(
        self, claims: List[Claim], reverts: List[Revert], allowed_npis=[]
    ):
        """
        Process claims and reverts, returning:
        - data: A dictionary by (npi, ndc) with aggregated metrics -> fills, reverted, total_price, total_quantity
        """
        claims_by_id = {}
        data = {}

        for claim in claims:
            if allowed_npis:
                if claim.npi not in allowed_npis:
                    logging.debug(
                        f"Ignored claim {claim.npi} because it's not included in the allowed npis list"
                    )
                    continue

            if claim.id in claims_by_id:
                logging.debug(f"Ignored claim {claim.npi} because it's duplicated")
                continue

            key = (claim.npi, claim.ndc)

            claims_by_id[claim.id] = {
                "key": key,
                "price": claim.price,
                "quantity": claim.quantity,
            }

            if key in data.keys():
                data[key]["fills"] += 1
                data[key]["total_price"] += claim.price
                data[key]["total_quantity"] += claim.quantity
            else:
                data[key] = {
                    "fills": 1,
                    "reverted": 0,
                    "total_price": claim.price,
                    "total_quantity": claim.quantity,
                }

        # Process reverts
        for revert in reverts:
            if revert.claim_id not in claims_by_id:
                logging.debug(
                    f"Ignored revert {revert.id} because there is no valid claim_id linked to it"
                )
                continue
            claim_data = claims_by_id[revert.claim_id]
            claim_key = claim_data["key"]
            data[claim_key]["total_price"] -= claim_data["price"]
            data[claim_key]["total_quantity"] -= claim_data["quantity"]
            data[claim_key]["fills"] -= 1
            data[claim_key]["reverted"] += 1

        return data

    def compute_metrics(
        self, claims: List[Claim], reverts: List[Revert], allowed_npis=[]
    ):
        results = []
        data = self.__process_claims_and_reverts(
            claims=claims, reverts=reverts, allowed_npis=allowed_npis
        )

        for key_data, value in data.items():
            if value["total_quantity"] > 0:
                avg_price = value["total_price"] / value["total_quantity"]
            else:
                avg_price = 0.0

            results.append(
                {
                    "npi": key_data[0],  # npi
                    "ndc": key_data[1],  # ndc
                    "fills": value["fills"],
                    "reverted": value["reverted"],
                    "avg_price": round(avg_price, 2),
                    "total_price": round(value["total_price"], 2),
                }
            )

        return results

    def drug_recommendation_by_chains(
        self,
        claims: List[Claim],
        reverts: List[Revert],
        pharmacies: List[Pharmacy],
        allowed_npis=[],
    ):

        data = self.__process_claims_and_reverts(
            claims=claims, reverts=reverts, allowed_npis=allowed_npis
        )  # data: (npi, npc) ->  fills, reverted, total_price, total_quantity

        npi_to_chain = {}
        for pharmacy in pharmacies:
            npi_to_chain[pharmacy.npi] = pharmacy.chain

        chain_data = {}  # ndc, chain -> total_price and total_quantity
        for (npi, ndc), metrics in data.items():
            if metrics["total_quantity"] <= 0 or npi not in npi_to_chain.keys():
                continue
            chain = npi_to_chain[npi]
            key = (ndc, chain)
            if key not in chain_data.keys():
                chain_data[key] = {
                    "total_price": metrics["total_price"],
                    "total_quantity": metrics["total_quantity"],
                }
            else:
                chain_data[key]["total_price"] += metrics["total_price"]
                chain_data[key]["total_quantity"] += metrics["total_quantity"]

        ndc_to_chains = {}  # ndc -> [(chain, avg_price)]
        for (ndc, chain), value in chain_data.items():
            avg_price = (
                value["total_price"] / value["total_quantity"]
                if value["total_quantity"] > 0
                else 0.0
            )
            # Here we have the result, we just need to map it to a dict structure using ndc
            if ndc not in ndc_to_chains.keys():
                ndc_to_chains[ndc] = [(chain, avg_price)]
            else:
                ndc_to_chains[ndc].append((chain, avg_price))

        results = []
        for ndc, chain_info in ndc_to_chains.items():
            chain_info.sort(key=lambda x: x[1])  # Here we order by avg_price
            formatted_chains = []
            for top_chain in chain_info[:2]:
                formatted_chains.append(
                    {"name": top_chain[0], "avg_price": round(top_chain[1], 2)}
                )
            results.append({"ndc": ndc, "chain": formatted_chains})

        return results

    def most_prescribed_quantity_by_drug(
        self, claims: List[Claim], reverts: List[Revert], allowed_npis=[]
    ):
        prescribed_drugs_by_quantity = {}
        results = []
        reverts_ids = [revert.claim_id for revert in reverts]
        for claim in claims:
            if claim.id in reverts_ids:
                continue

            if allowed_npis:
                if claim.npi not in allowed_npis:
                    logging.debug(
                        f"most_prescribed_quantity_by_drug: Ignored claim {claim.npi} because it's not included in the allowed npis list"
                    )
                    continue

            if claim.ndc not in prescribed_drugs_by_quantity.keys():
                prescribed_drugs_by_quantity[claim.ndc] = {claim.quantity: 1}
            elif claim.quantity in prescribed_drugs_by_quantity[claim.ndc].keys():
                prescribed_drugs_by_quantity[claim.ndc][claim.quantity] += 1
            else:
                prescribed_drugs_by_quantity[claim.ndc][claim.quantity] = 1

        for key, value in prescribed_drugs_by_quantity.items():
            most_prescribed_quantity_list = []
            sorted_by_value_desc = sorted(
                value.items(), key=lambda x: x[1], reverse=True
            )

            for quantity_key, times in sorted_by_value_desc:
                most_prescribed_quantity_list.append(quantity_key)
            ndc_result = {
                "ndc": key,
                "most_prescribed_quantity": most_prescribed_quantity_list,
            }
            results.append(ndc_result)

        return results
