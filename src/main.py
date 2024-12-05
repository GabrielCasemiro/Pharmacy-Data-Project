from models import Claim, Revert
import json

if __name__ == "__main__":
    print("Initializing script...")

    results = []
    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)
