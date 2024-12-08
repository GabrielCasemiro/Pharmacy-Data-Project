import csv
import json
import os
from .db_interface import DatabaseInterface
from src.models.claim import Claim
from src.models.revert import Revert
from src.models.pharmacy import Pharmacy
from typing import List
import logging


class JSONDatabase(DatabaseInterface):
    def __init__(self, claims_dir: str, reverts_dir: str, pharmacies_dir: str):
        self.claims_dir = claims_dir
        self.reverts_dir = reverts_dir
        self.pharmacies_dir = pharmacies_dir

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

    def retrieve_pharmacies(self) -> List[Pharmacy]:
        pharmacies = []
        for filename in os.listdir(self.pharmacies_dir):
            if filename.endswith(".csv"):
                filepath = os.path.join(self.pharmacies_dir, filename)

                with open(filepath, "r") as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        try:
                            pharmacy = Pharmacy(
                                chain=row["chain"].replace(" ", ""), npi=row["npi"]
                            )
                            pharmacies.append(pharmacy)
                        except Exception as ex:
                            logging.warning(
                                "Fail to process pharmacy record %s from file %s due to %s"
                                % (row, filepath, str(ex))
                            )
        return pharmacies
