from abc import ABC, abstractmethod
from ..models.claim import Claim
from ..models.revert import Revert
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
