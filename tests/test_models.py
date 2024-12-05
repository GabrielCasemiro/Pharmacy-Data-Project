import pytest
from pydantic import ValidationError
from datetime import datetime
from src.models.claim import Claim
from src.models.revert import Revert


def test_valid_claim():
    claim_data = {
        "id": "9b778873-d84d-497b-8c04-f0de70c302a7",
        "npi": "44423452",
        "ndc": "00093752910",
        "price": 60849.0,
        "quantity": 90.0,
        "timestamp": "2024-03-01T21:09:01",
    }
    claim = Claim(**claim_data)
    assert claim.id == "9b778873-d84d-497b-8c04-f0de70c302a7"
    assert claim.npi == "44423452"
    assert claim.ndc == "00093752910"
    assert claim.price == 60849.0
    assert claim.quantity == 90.0
    assert claim.timestamp == datetime(
        year=2024, month=3, day=1, hour=21, minute=9, second=1
    )


def test_invalid_claim_missing_fields():
    invalid_claim_data = {
        "id": "invalid_id",
        "npi": "2334",
        "ndc": "00000000000",
        "timestamp": "2023-09-01T21:09:01",
    }
    with pytest.raises(ValidationError):
        Claim(**invalid_claim_data)


def test_valid_revert():
    revert_data = {
        "id": "509ec2fe-f2db-4da0-bef3-9cb4fd54dfe7",
        "claim_id": "983ccb14-dacd-49f7-9ddb-a5299ed6cdb7",
        "timestamp": "2022-06-02T01:11:19",
    }
    revert = Revert(**revert_data)
    assert revert.id == "509ec2fe-f2db-4da0-bef3-9cb4fd54dfe7"
    assert revert.claim_id == "983ccb14-dacd-49f7-9ddb-a5299ed6cdb7"
    assert revert.timestamp == datetime(
        year=2022, month=6, day=2, hour=1, minute=11, second=19
    )


def test_invalid_revert_missing_claim_id():
    invalid_revert_data = {
        "id": "invalid_revert_idp",
        "timestamp": "2022-06-02T01:11:19",
    }
    with pytest.raises(ValidationError):
        Revert(**invalid_revert_data)
