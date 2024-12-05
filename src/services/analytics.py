import logging
from ..models.claim import Claim
from ..models.revert import Revert
from analytics_interface import AnalyticsInterface
from typing import List
import json


class Analytics(AnalyticsInterface):
    def __init__(self, allowed_npis) -> None:
        self.allowed_npis = allowed_npis

    def compute_metrics(self, claims: List[Claim], reverts: List[Revert]):
        results = []
        data = {}

        # compute claims
        results.append(
            {
                "npi": "1234",
                "ndc": "12345",
                "fills": 1,
                "reverted": 2,
                "avg_price": 123.4,
                "total_price": 123.4,
            }
        )
        logging.info(
            "Claims compute before reverts: %s" % json.dumps(results, indent=2)
        )

        # compute reverts
        logging.info("Claims compute after reverts: %s" % json.dumps(results, indent=2))

        return results
