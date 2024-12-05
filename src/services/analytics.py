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

        # logging.info("Claims compute before reverts: %s" % data.values())

        # # compute reverts
        # logging.info("Claims compute after reverts: %s" % data)

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
                    "avg_price": avg_price,
                    "total_price": value["total_price"],
                }
            )

        return results
