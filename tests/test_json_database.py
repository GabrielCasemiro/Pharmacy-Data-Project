import json
import logging
import pytest
from src.repository.json_database import JSONDatabase
from src.models.claim import Claim
from src.models.revert import Revert
from src.models.pharmacy import Pharmacy

import sys


@pytest.fixture
def setup_directories(tmp_path):
    pharmacies_dir = tmp_path / "pharmacies"
    pharmacies_dir.mkdir()
    csv_content = """chain,npi
    health,1234567890
    saint,0987654321
    """
    (pharmacies_dir / "pharmacies_file.csv").write_text(csv_content)

    claims_dir = tmp_path / "claims"
    reverts_dir = tmp_path / "reverts"
    claims_dir.mkdir()
    reverts_dir.mkdir()
    return (claims_dir, reverts_dir, pharmacies_dir)


def test_retrieve_claims_success(setup_directories):
    claims_dir, reverts_dir, pharmacies_dir = setup_directories
    valid_claim = {
        "id": "01000101",
        "npi": "125234",
        "ndc": "00093755",
        "price": 20.0,
        "quantity": 50.0,
        "timestamp": "2024-03-01T21:09:01",
    }

    (claims_dir / "claims_file.json").write_text(json.dumps([valid_claim]))

    db = JSONDatabase(
        claims_dir=str(claims_dir),
        reverts_dir=str(reverts_dir),
        pharmacies_dir=str(pharmacies_dir),
    )
    claims = db.retrieve_claims()

    assert len(claims) == 1
    assert isinstance(claims[0], Claim)
    assert claims[0].id == "01000101"
    assert claims[0].price == 20.0


def test_retrieve_claims_invalid_record(setup_directories, caplog):
    claims_dir, reverts_dir, pharmacies_dir = setup_directories
    invalid_claim = {"id": "invalid-claim-id", "timestamp": "2024-03-01T21:09:01"}
    (claims_dir / "claims_file.json").write_text(json.dumps([invalid_claim]))
    db = JSONDatabase(
        claims_dir=str(claims_dir),
        reverts_dir=str(reverts_dir),
        pharmacies_dir=str(pharmacies_dir),
    )

    with caplog.at_level(logging.WARNING):
        claims = db.retrieve_claims()

    assert len(claims) == 0
    assert "Fail to process record" in caplog.text


def test_retrieve_reverts_success(setup_directories):
    claims_dir, reverts_dir, pharmacies_dir = setup_directories
    valid_revert = {
        "id": "02340203",
        "claim_id": "01000101",
        "timestamp": "2024-05-02T21:41:19",
    }
    (reverts_dir / "reverts_file.json").write_text(json.dumps([valid_revert]))
    db = JSONDatabase(
        claims_dir=str(claims_dir),
        reverts_dir=str(reverts_dir),
        pharmacies_dir=str(pharmacies_dir),
    )
    reverts = db.retrieve_reverts()

    assert len(reverts) == 1
    assert isinstance(reverts[0], Revert)
    assert reverts[0].id == "02340203"
    assert reverts[0].claim_id == "01000101"


def test_retrieve_reverts_invalid_record(setup_directories, caplog):
    claims_dir, reverts_dir, pharmacies_dir = setup_directories
    invalid_revert = {"id": "revert-invalid", "timestamp": "2022-01-02T11:41:19"}
    (reverts_dir / "reverts_file.json").write_text(json.dumps([invalid_revert]))
    db = JSONDatabase(
        claims_dir=str(claims_dir),
        reverts_dir=str(reverts_dir),
        pharmacies_dir=str(pharmacies_dir),
    )

    with caplog.at_level(logging.WARNING):
        reverts = db.retrieve_reverts()

    assert len(reverts) == 0
    assert "Fail to process record" in caplog.text


def test_retrieve_pharmacies_success(setup_directories):
    claims_dir, reverts_dir, pharmacies_dir = setup_directories
    db = JSONDatabase(
        claims_dir=str(claims_dir),
        reverts_dir=str(reverts_dir),
        pharmacies_dir=str(pharmacies_dir),
    )
    pharmacies = db.retrieve_pharmacies()

    assert len(pharmacies) == 2
    assert isinstance(pharmacies[0], Pharmacy)
    assert pharmacies[0].chain == "health"
    assert pharmacies[0].npi == "1234567890"
    assert pharmacies[1].chain == "saint"
    assert pharmacies[1].npi == "0987654321"
