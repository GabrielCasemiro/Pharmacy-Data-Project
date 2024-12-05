import json
from .repository.json_database import JSONDatabase as Database
import logging
import os

# Configure logging: set the level and format
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
    db_obj = Database(claims_dir=claims_dir, reverts_dir=reverts_dir)

    claims = db_obj.retrieve_claims()
    logging.info(f"Number of claims retrieved: {len(claims)}")
    reverts = db_obj.retrieve_reverts()
    logging.info(f"Number of reverts retrieved: {len(reverts)}")

    results = []
    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)
