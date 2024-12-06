import logging
from ..models.claim import Claim
from ..models.revert import Revert
from .analytics_interface import AnalyticsInterface
from typing import List
import json


class Analytics(AnalyticsInterface):
    def __init__(self, allowed_npis) -> None:
        self.allowed_npis = allowed_npis

    def compute_metrics(self, claims: List[Claim], reverts: List[Revert]):
        results = []
        data = {}
        claims_by_id = {}

        # compute claims
        for claim in claims:
            if claim.npi not in self.allowed_npis:
                logging.info(
                    f"Ignored claim {claim.npi} because it's not included in the allowed npis list"
                )
                continue

            if claim.id in claims_by_id.keys():
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

        for revert in reverts:
            if revert.claim_id not in claims_by_id.keys():
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
