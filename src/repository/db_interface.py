from abc import ABC, abstractmethod
from src.models.claim import Claim
from src.models.revert import Revert
from typing import List


class DatabaseInterface(ABC):
    @abstractmethod
    def retrieve_claims(self) -> List[Claim]:
        """Read claims data from the source"""
        pass

    @abstractmethod
    def retrieve_reverts(self) -> List[Revert]:
        """Read revert events from the data source"""
        pass

    @abstractmethod
    def retrieve_pharmacies(self) -> List[Revert]:
        """Read pharmacies from the data source"""
        pass
