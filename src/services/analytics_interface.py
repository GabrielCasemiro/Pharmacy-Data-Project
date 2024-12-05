from abc import ABC, abstractmethod
from ..models.claim import Claim
from ..models.revert import Revert
from typing import List, Dict


class AnalyticsInterface(ABC):
    @abstractmethod
    def compute_metrics(self, claims=List[Claim], reverts=List[Revert]) -> List[Dict]:
        """Compute metrics based on claims and reverts"""
        pass
