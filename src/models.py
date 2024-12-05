from pydantic import BaseModel
from datetime import datetime


class Claim(BaseModel):
    id: str
    npi: str
    ndc: str
    price: float
    quantity: float
    timestamp: datetime


class Revert(BaseModel):
    id: str
    claim_id: str
    timestamp: datetime


class Pharmacy(BaseModel):
    id: str
    chain: str
