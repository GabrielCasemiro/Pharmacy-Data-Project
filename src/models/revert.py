from pydantic import BaseModel
from datetime import datetime


class Revert(BaseModel):
    id: str
    claim_id: str
    timestamp: datetime
