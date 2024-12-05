import json
import os
from .db_interface import DatabaseInterface
from ..models.claim import Claim
from ..models.revert import Revert
from typing import List
import logging


class JSONDatabase(DatabaseInterface):
    def __init__(self, claims_dir: str, reverts_dir: str):
        self.claims_dir = claims_dir
        self.reverts_dir = reverts_dir

    def retrieve_claims(self) -> List[Claim]:
        claims = []
        for filename in os.listdir(self.claims_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.claims_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    for record in data:
                        try:
                            claim = Claim(**record)
                            claims.append(claim)
                        except Exception as ex:
                            logging.warning(
                                "Fail to process record %s from file %s due to %s"
                                % (record, filepath, str(ex))
                            )
        return claims

    def retrieve_reverts(self) -> List[Revert]:
        reverts = []
        for filename in os.listdir(self.reverts_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.reverts_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    for record in data:
                        try:
                            revert = Revert(**record)
                            reverts.append(revert)
                        except Exception as ex:
                            logging.warning(
                                "Fail to process record %s from file %s due to %s"
                                % (record, filepath, str(ex))
                            )
        return reverts
