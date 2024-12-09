import csv
import json
import os
from .db_interface import DatabaseInterface
from src.models.claim import Claim
from src.models.revert import Revert
from src.models.pharmacy import Pharmacy
from typing import List
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def load_claims_from_file(filepath: str) -> List[Claim]:
    results = []
    with open(filepath, "r") as f:
        data = json.load(f)
        for record in data:
            try:
                claim = Claim(**record)
                results.append(claim)
            except Exception as ex:
                logger.warning(
                    "Fail to process claim record %s from file %s due to %s"
                    % (record, filepath, str(ex))
                )
    return results


def load_reverts_from_file(filepath: str) -> List[Revert]:
    results = []
    with open(filepath, "r") as f:
        data = json.load(f)
        for record in data:
            try:
                revert = Revert(**record)
                results.append(revert)
            except Exception as ex:
                logger.warning(
                    "Fail to process revert record %s from file %s due to %s"
                    % (record, filepath, str(ex))
                )
    return results


def load_pharmacies_from_file(filepath: str) -> List[Pharmacy]:
    results = []
    with open(filepath, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                pharmacy = Pharmacy(chain=row["chain"].replace(" ", ""), npi=row["npi"])
                results.append(pharmacy)
            except Exception as ex:
                logger.warning(
                    "Fail to process pharmacy record %s from file %s due to %s"
                    % (row, filepath, str(ex))
                )
    return results


class JSONDatabaseParallel(DatabaseInterface):
    def __init__(self, claims_dir: str, reverts_dir: str, pharmacies_dir: str):
        self.claims_dir = claims_dir
        self.reverts_dir = reverts_dir
        self.pharmacies_dir = pharmacies_dir

    def retrieve_claims(self) -> List[Claim]:
        files = [
            os.path.join(self.claims_dir, f)
            for f in os.listdir(self.claims_dir)
            if f.endswith(".json")
        ]
        claims = []
        if files:
            with ProcessPoolExecutor() as executor:
                futures = {
                    executor.submit(load_claims_from_file, fp): fp for fp in files
                }
                for future in as_completed(futures):
                    claims.extend(future.result())
        return claims

    def retrieve_reverts(self) -> List[Revert]:
        files = [
            os.path.join(self.reverts_dir, f)
            for f in os.listdir(self.reverts_dir)
            if f.endswith(".json")
        ]
        reverts = []
        if files:
            with ProcessPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(load_reverts_from_file, fp): fp for fp in files
                }
                for future in as_completed(futures):
                    reverts.extend(future.result())
        return reverts

    def retrieve_pharmacies(self) -> List[Pharmacy]:
        files = [
            os.path.join(self.pharmacies_dir, f)
            for f in os.listdir(self.pharmacies_dir)
            if f.endswith(".csv")
        ]
        pharmacies = []

        for filepath in files:
            pharmacies.extend(load_pharmacies_from_file(filepath))
        return pharmacies
