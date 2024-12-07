from pydantic import BaseModel


class Pharmacy(BaseModel):
    chain: str
    npi: str
