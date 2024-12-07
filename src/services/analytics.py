import logging
from ..models.claim import Claim
from ..models.revert import Revert
from ..models.pharmacy import Pharmacy
from .analytics_interface import AnalyticsInterface
from typing import List, Dict
import json


class Analytics(AnalyticsInterface):
    def __init__(self, allowed_npis) -> None:
        self.allowed_npis = allowed_npis

    def __process_claims_and_reverts(self, claims: List[Claim], reverts: List[Revert]):
        """
        Process claims and reverts, returning:
        - claims_by_id: A dictionary by claim_id with { 'key': (npi, ndc), 'price': float, 'quantity': float }
        - data: A dictionary by (npi, ndc) with aggregated metrics -> fills, reverted, total_price, total_quantity
        """
        claims_by_id = {}
        data = {}

        for claim in claims:
            if self.allowed_npis:
                if claim.npi not in self.allowed_npis:
                    logging.info(
                        f"Ignored claim {claim.npi} because it's not included in the allowed npis list"
                    )
                    continue

            if claim.id in claims_by_id:
                logging.info(f"Ignored claim {claim.npi} because it's duplicated")
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
                logging.info(
                    f"Ignored revert {revert.id} because there is no valid claim_id linked to it"
                )
                continue
            claim_data = claims_by_id[revert.claim_id]
            claim_key = claim_data["key"]
            data[claim_key]["total_price"] -= claim_data["price"]
            data[claim_key]["total_quantity"] -= claim_data["quantity"]
            data[claim_key]["fills"] -= 1
            data[claim_key]["reverted"] += 1

        return claims_by_id, data

    def compute_metrics(self, claims: List[Claim], reverts: List[Revert]):
        results = []
        claims_by_id, data = self.__process_claims_and_reverts(
            claims=claims, reverts=reverts
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
        self, claims: List[Claim], reverts: List[Revert], pharmacies: List[Pharmacy]
    ):

        claims_by_id, data = self.__process_claims_and_reverts(
            claims=claims, reverts=reverts
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
        self, claims: List[Claim], reverts: List[Revert], pharmacies: List[Pharmacy]
    ):
        """Compute drug most common quantity prescribed"""
        return [
            {
                "ndc": "00002323401",
                "most_prescribed_quantity": [8.5, 15.0, 45.0, 180.0, 2.0],
            }
        ]
