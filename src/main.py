import json
from .repository.json_database import JSONDatabase as Database
from .services.analytics import Analytics as AnalyticsService
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.info("Initializing script...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    claims_dir = os.path.join(project_root, "data", "claims")
    reverts_dir = os.path.join(project_root, "data", "reverts")
    pharmacies_dir = os.path.join(project_root, "data", "reverts")

    db_obj = Database(claims_dir=claims_dir, reverts_dir=reverts_dir)

    claims = db_obj.retrieve_claims()
    logging.info(f"Number of claims retrieved: {len(claims)}")
    reverts = db_obj.retrieve_reverts()
    logging.info(f"Number of reverts retrieved: {len(reverts)}")
    pharmacies = []  # db_obj.pharmacies()
    npis_list = [
        "1234567890",
        "0987654321",
        "5678901234",
        "4567890123",
        "3456789012",
        "8901234567",
        "0123456789",
        "7890123456",
        "1111111111",
        "4444444444",
        "7777777777",
        "2222222222",
        "5555555555",
        "8888888888",
        "3333333333",
        "6666666666",
        "9999999999",
    ]
    analytics_service = AnalyticsService(allowed_npis=npis_list)

    results = analytics_service.compute_metrics(claims=claims, reverts=reverts)
    logging.info("Saving results to output.json")
    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)
    logging.info("Results has been saved succesfully")
