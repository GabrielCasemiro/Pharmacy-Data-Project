import sys, os, time
import argparse
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.repository.json_database import JSONDatabase as Database
from src.services.analytics_parallel import Analytics as AnalyticsService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    start = time.perf_counter()
    parser = argparse.ArgumentParser(description="Pharmacy Data Project")
    parser.add_argument(
        "--goals",
        nargs="*",
        default=["2", "3", "4"],
        help="Specify which goals to run (2, 3, and/or 4). By default, all are run.",
    )
    args = parser.parse_args()

    # Determine which goals to run
    run_goal_2 = "2" in args.goals
    run_goal_3 = "3" in args.goals
    run_goal_4 = "4" in args.goals

    logging.info("Initializing script...")
    output_file_list = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    claims_dir = os.path.join(project_root, "data", "claims")
    reverts_dir = os.path.join(project_root, "data", "reverts")
    pharmacies_dir = os.path.join(project_root, "data", "pharmacies")

    # Ensure output directory exists
    output_dir = os.path.join(project_root, "data", "outputs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    db_obj = Database(
        claims_dir=claims_dir, reverts_dir=reverts_dir, pharmacies_dir=pharmacies_dir
    )

    claims = db_obj.retrieve_claims() * 100
    logging.info(f"Number of claims retrieved: {len(claims)}")
    reverts = db_obj.retrieve_reverts() * 100
    logging.info(f"Number of reverts retrieved: {len(reverts)}")
    pharmacies = db_obj.retrieve_pharmacies()
    npis_list = [pharmacy.npi for pharmacy in pharmacies]

    analytics_service = AnalyticsService()

    # Goal 2: Compute metrics
    if run_goal_2:
        metrics = analytics_service.compute_metrics(claims=claims, reverts=reverts)
        output_file_list.append({"filename": "metrics", "value": metrics})

    # Goal 3: Drug recommendation by chains
    if run_goal_3:
        drug_recommendation_by_chains = analytics_service.drug_recommendation_by_chains(
            claims=claims,
            reverts=reverts,
            pharmacies=pharmacies,
            allowed_npis=npis_list,
        )
        output_file_list.append(
            {
                "filename": "drug_recommendation_by_chains",
                "value": drug_recommendation_by_chains,
            }
        )

    # Goal 4: Most prescribed quantity by drug
    if run_goal_4:
        most_prescribed_quantity_by_drug = (
            analytics_service.most_prescribed_quantity_by_drug(
                claims=claims, reverts=reverts
            )
        )
        output_file_list.append(
            {
                "filename": "most_prescribed_quantity_by_drug",
                "value": most_prescribed_quantity_by_drug,
            }
        )
    end = time.perf_counter()

    print(f"JSONDatabaseParallel load time: {end - start:.2f} seconds")
    # Save results to data/outputs
    for result in output_file_list:
        output_path = os.path.join(output_dir, f"{result['filename']}.json")
        logging.info(f"Saving results to {output_path}")
        with open(output_path, "w") as f:
            json.dump(result["value"], f, indent=2)
        logging.info("Results have been saved successfully")
