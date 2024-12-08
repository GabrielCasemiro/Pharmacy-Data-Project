import pytest
from src.services.analytics import Analytics
from src.models.claim import Claim
from src.models.revert import Revert
from src.models.pharmacy import Pharmacy


def test_single_claim_no_revert():
    allowed_npis = {"4444444444"}
    analytics = Analytics()

    result = analytics.compute_metrics(
        claims=[
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f0de70c302a7",
                    "ndc": "00093752910",
                    "npi": "4444444444",
                    "quantity": 90.0,
                    "price": 60849.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            )
        ],
        reverts=[],
        allowed_npis=allowed_npis,
    )
    assert len(result) == 1
    assert result[0]["npi"] == "4444444444"
    assert result[0]["ndc"] == "00093752910"
    assert result[0]["fills"] == 1
    assert result[0]["reverted"] == 0
    assert result[0]["avg_price"] == 676.1
    assert result[0]["total_price"] == 60849.0


def test_claim_with_revert():
    allowed_npis = {"4444444444"}
    analytics = Analytics()

    result = analytics.compute_metrics(
        claims=[
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f0de70c302a7",
                    "ndc": "00093752910",
                    "npi": "4444444444",
                    "quantity": 90.0,
                    "price": 60849.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            )
        ],
        reverts=[
            Revert(
                **{
                    "id": "509ec2fe-f2db-4da0-bef3-9cb4fd54dfe7",
                    "claim_id": "9b778873-d84d-497b-8c04-f0de70c302a7",
                    "timestamp": "2024-04-02T21:41:19",
                },
            )
        ],
        allowed_npis=allowed_npis,
    )
    assert len(result) == 1
    assert result[0]["npi"] == "4444444444"
    assert result[0]["ndc"] == "00093752910"
    assert result[0]["fills"] == 0
    assert result[0]["reverted"] == 1
    assert result[0]["avg_price"] == 0.0
    assert result[0]["total_price"] == 0.0


def tests_multiple_reverts_and_claims():
    allowed_npis = {"4444444444", "123452523", "123452522343"}
    analytics = Analytics()

    results = analytics.compute_metrics(
        claims=[
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f0de70c302a7",
                    "ndc": "00093752910",
                    "npi": "4444444444",
                    "quantity": 90.0,
                    "price": 60849.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            ),
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f1235252",
                    "ndc": "1422343245",
                    "npi": "123452523",
                    "quantity": 5.0,
                    "price": 10.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            ),
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f12352524",
                    "ndc": "1422343245",
                    "npi": "123452523",
                    "quantity": 1.0,
                    "price": 10.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            ),
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f3525245",
                    "ndc": "14223432423425",
                    "npi": "123452522343",
                    "quantity": 100.0,
                    "price": 2342.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            ),
        ],
        reverts=[
            Revert(
                **{
                    "id": "509ec2fe-f2db-4da0-bef3-9cb4fd54dfe7",
                    "claim_id": "9b778873-d84d-497b-8c04-f0de70c302a7",
                    "timestamp": "2024-04-02T21:41:19",
                },
            ),
            Revert(
                **{
                    "id": "509ec2fe-f2db-4da0-bef3-9cb4fd54dfe7",
                    "claim_id": "9b778873-d84d-497b-8c04-f1235252",
                    "timestamp": "2024-04-02T21:41:19",
                },
            ),
        ],
        allowed_npis=allowed_npis,
    )
    assert len(results) == 3
    keys = []
    for result in results:
        if result["npi"] == "4444444444" and result["ndc"] == "00093752910":
            assert result["npi"] == "4444444444"
            assert result["ndc"] == "00093752910"
            assert result["fills"] == 0
            assert result["reverted"] == 1
            assert result["avg_price"] == 0.0
            assert result["total_price"] == 0.0
        elif result["npi"] == "123452523" and result["ndc"] == "1422343245":
            assert result["npi"] == "123452523"
            assert result["ndc"] == "1422343245"
            assert result["fills"] == 1
            assert result["reverted"] == 1
            assert result["avg_price"] == 10.0
            assert result["total_price"] == 10.0
        elif result["npi"] == "123452522343" and result["ndc"] == "14223432423425":
            assert result["npi"] == "123452522343"
            assert result["ndc"] == "14223432423425"
            assert result["fills"] == 1
            assert result["reverted"] == 0
            assert result["avg_price"] == 23.42
            assert result["total_price"] == 2342.0
        keys.append((result["npi"], result["ndc"]))

    assert ("123452522343", "14223432423425") in keys
    assert ("123452523", "1422343245") in keys
    assert ("4444444444", "00093752910") in keys


def test_claim_non_allowed_npi():
    allowed_npis = {"4444444444"}
    analytics = Analytics()

    result = analytics.compute_metrics(
        claims=[
            Claim(
                **{
                    "id": "9b778873-d84d-497b-8c04-f0de70c302a7",
                    "ndc": "00093752910",
                    "npi": "111111111",
                    "quantity": 90.0,
                    "price": 60849.0,
                    "timestamp": "2024-03-01T21:09:01",
                }
            )
        ],
        reverts=[],
        allowed_npis=allowed_npis,
    )
    assert len(result) == 0


def test_drug_recommendation_by_chains_simple():
    # Allowed NPIs (pharmacies)
    allowed_npis = {"1234567890", "7890123456", "2222222222"}
    analytics = Analytics()

    # Pharmacies and their chains
    pharmacies = [
        Pharmacy(chain="health", npi="1234567890"),
        Pharmacy(chain="saint", npi="7890123456"),
        Pharmacy(chain="doctor", npi="2222222222"),
    ]

    # Claims for a single NDC from three different chains
    # saint: total_ice=100, total_quantity=5 => avg=20.0
    # doctor: total_price=210, total_quantity=10 => avg=21.0
    # health: total_price=300, total_quantity=10 => avg=30.0
    claims = [
        Claim(
            id="194c7bbc-c9f6-4d6f-a4c7-83028ae2c857",
            ndc="00015066812",
            npi="1234567890",
            quantity=10.0,
            price=300.0,
            timestamp="2024-03-01T21:09:01",
        ),
        Claim(
            id="204c7bbc-c9f6-4d6f-a4c7-83028ae2c852",
            ndc="00015066812",
            npi="7890123456",
            quantity=5.0,
            price=100.0,
            timestamp="2024-03-01T21:09:01",
        ),
        Claim(
            id="214c7bbc-c9f6-4d6f-a4c7-83028ae2c853",
            ndc="00015066812",
            npi="2222222222",
            quantity=10.0,
            price=210.0,
            timestamp="2024-03-01T21:09:01",
        ),
    ]

    reverts = []

    results = analytics.drug_recommendation_by_chains(
        claims=claims, reverts=reverts, pharmacies=pharmacies
    )

    # We expect:
    # NDC: 00015066812
    # Chains sorted by avg_price: saint(20.0), doctor(21.0), health(30.0)

    assert len(results) == 1
    assert results[0]["ndc"] == "00015066812"
    top_chains = results[0]["chain"]
    assert len(top_chains) == 2

    # Check top two chains
    assert top_chains[0]["name"] == "saint"
    assert top_chains[0]["avg_price"] == 20.0
    assert top_chains[1]["name"] == "doctor"
    assert top_chains[1]["avg_price"] == 21.0
