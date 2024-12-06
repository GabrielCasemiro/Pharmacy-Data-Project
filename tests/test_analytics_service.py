import pytest
from src.services.analytics import Analytics
from src.models.claim import Claim
from src.models.revert import Revert


def test_single_claim_no_revert():
    allowed_npis = {"4444444444"}
    analytics = Analytics(allowed_npis=allowed_npis)

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
    analytics = Analytics(allowed_npis=allowed_npis)

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
    analytics = Analytics(allowed_npis=allowed_npis)

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
    analytics = Analytics(allowed_npis=allowed_npis)

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
    )
    assert len(result) == 0
