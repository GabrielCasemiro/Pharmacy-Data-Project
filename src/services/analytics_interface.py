from abc import ABC, abstractmethod
from src.models.claim import Claim
from src.models.revert import Revert
from src.models.pharmacy import Pharmacy
from typing import List, Dict


class AnalyticsInterface(ABC):
    @abstractmethod
    def compute_metrics(self, claims=List[Claim], reverts=List[Revert]) -> List[Dict]:
        """Compute metrics based on claims and reverts"""
        pass

    @abstractmethod
    def drug_recommendation_by_chains(
        self, claims: List[Claim], reverts: List[Revert], pharmacies: List[Pharmacy]
    ) -> List[Dict]:
        """Compute drug unit prices per Chain"""
        pass

    @abstractmethod
    def most_prescribed_quantity_by_drug(
        self, claims: List[Claim], reverts: List[Revert]
    ) -> List[Dict]:
        """Compute drug most common quantity prescribed"""
        pass
