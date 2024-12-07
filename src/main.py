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
    output_file_list = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    claims_dir = os.path.join(project_root, "data", "claims")
    reverts_dir = os.path.join(project_root, "data", "reverts")
    pharmacies_dir = os.path.join(project_root, "data", "pharmacies")

    db_obj = Database(
        claims_dir=claims_dir, reverts_dir=reverts_dir, pharmacies_dir=pharmacies_dir
    )

    claims = db_obj.retrieve_claims()
    logging.info(f"Number of claims retrieved: {len(claims)}")
    reverts = db_obj.retrieve_reverts()
    logging.info(f"Number of reverts retrieved: {len(reverts)}")
    pharmacies = db_obj.retrieve_pharmacies()
    npis_list = [pharmacy.npi for pharmacy in pharmacies]
    analytics_service = AnalyticsService(allowed_npis=npis_list)

    metrics = analytics_service.compute_metrics(claims=claims, reverts=reverts)
    output_file_list.append({"filename": "metrics", "value": metrics})
    drug_recommendation_by_chains = analytics_service.drug_recommendation_by_chains(
        claims=claims, reverts=reverts, pharmacies=pharmacies
    )
    output_file_list.append(
        {
            "filename": "drug_recommendation_by_chains",
            "value": drug_recommendation_by_chains,
        }
    )
    # most_prescribed_quantity_by_drug = (
    #     analytics_service.most_prescribed_quantity_by_drug(
    #         claims=claims, reverts=reverts, pharmacies=pharmacies
    #     )
    # )
    for result in output_file_list:
        logging.info("Saving results to metrics.json")
        with open("%s.json" % result["filename"], "w") as f:
            json.dump(result["value"], f, indent=2)
        logging.info("Results has been saved succesfully")
