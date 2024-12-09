# Pharmacy-Data-Project

This project processes pharmacy claims, revert events, and pharmacy data to compute various metrics and insights:
1. **Metrics for some dimensions (Goal 2):** Calculated metrics such as fills, reverted claims, average unit price, and total price per `(npi, ndc)`.
2. **Drug Recommendation by Chains (Goal 3):** Identifies the top two cheapest chains per drug based on average unit price.
3. **Most Prescribed Quantity by Drug (Goal 4):** Lists the most common prescribed quantities per drug to help negotiate price discounts.

## Project Structure
```
project/
├─ data/
│  ├─ claims/      # JSON claims files
│  ├─ reverts/     # JSON reverts files
│  └─ pharmacies/  # CSV file mapping npis to chains
│  └─ outputs/     # JSON output files for goals 2, 3, and 4
│     └─ metrics.json                          # Output for Goal 2
│     └─ drug_recommendation_by_chains.json    # Output for Goal 3
│     └─ most_prescribed_quantity_by_drug.json # Output for Goal 4
├─ src/
│  ├─ init.py
│  ├─ main.py        # Entry point of the application
│  ├─ models/        # Pydantic models (Claim, Revert, Pharmacy)
│  ├─ repository/    # Data retrieval (JSONDatabase, etc.)
│  └─ services/      # Analytics services (Analytics class)
├─ tests/             # Unit tests
└─ requirements.txt   # Python dependencies
```

## Prerequisites

- Python 3.8+ installed
- `pip` to install dependencies
- Docker (if you want to run using Docker)


## Why Pydantic?

This project uses [Pydantic](https://pydantic-docs.helpmanual.io/) models (in `src/models`) to define the schema for Claims, Reverts, and Pharmacy records. Pydantic ensures that each record entering the processing pipeline adheres to a defined schema. This provides a few key benefits:

1. **Data Validation:**  
   Before any processing steps occur, each record is validated against the Pydantic model. Invalid data is either corrected or excluded early on, preventing corrupt or malformed data from reaching deeper stages of the pipeline.

2. **Consistent Types and Structure:**  
   By enforcing a strict schema, all processing steps can rely on data having a consistent structure and type. For example, `price` is always a float and `timestamp` is always a valid datetime. This consistency reduces errors and simplifies the logic in the analytics steps.

3. **Easier Debugging and Maintenance:**  
   When the data schema is well-defined and enforced, it’s easier to pinpoint issues if something goes wrong. Developers can be confident that unexpected behavior is likely not caused by malformed data, because Pydantic has already enforced the schema rules

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:GabrielCasemiro/Pharmacy-Data-Project.git
   cd Pharmacy-Data-Project


### Virtual Environment Setup
It’s recommended to create a Python virtual environment to isolate the project’s dependencies.

1.	Create a virtual environment:
```
python3 -m virtualenv venv
```

2. Activate virtualenv 
```
source venv/bin/activate
```

3. You can install all dependencies using:
```
pip install requirements.txt
```

### Running the Application

Make sure your data directory is populated with:
- data/claims/*.json
- data/reverts/*.json
- data/pharmacies/*.csv

Then run :
```
python3 src/main.py
```
This will run all goals (2, 3, and 4) by default.

The application will:
- Process claims and reverts.
- Generate the metrics.json file for Goal 2.
- Generate drug_recommendation_by_chains.json for Goal 3. (For this goal, only the pharmacies listed in the pharmacies csv files will be considered)
- Generate most_prescribed_quantity_by_drug.json for Goal 4.

### Running Specific Goals

You can specify which goals to run using the --goals argument:
```
python3 src/main.py --goals 2 3
```
This will run only Goal 2 and Goal 3. Similarly:
- --goals 2 runs only Goal 2.
- --goals 3 runs only Goal 3.
- --goals 4 runs only Goal 4.
- --goals 2 4 runs Goals 2 and 4, skipping Goal 3.

### Testing


To run tests, make sure you are in the project’s root directory and that your virtual environment is activated. Run:

```
pytest tests
```

### Running with Docker

1. Build the docker image 
```
docker build -t pharmacy-data-project:latest .
```

2.	Run the container:
```
docker run --rm -v $(pwd)/data:/app/data -v $(pwd):/app pharmacy-data-project:latest
```

After the container finishes, you should see the output files (metrics.json, drug_recommendation_by_chains.json, most_prescribed_quantity_by_drug.json) in your local directory.

### Outputs
- metrics.json (Goal 2): Contains aggregated metrics by (npi, ndc).
- drug_recommendation_by_chains.json (Goal 3): Shows the top 2 cheapest chains per drug.(For this goal, only the pharmacies listed in the pharmacies csv files will be considered)
- most_prescribed_quantity_by_drug.json (Goal 4): Lists the most common prescribed quantities per drug.
#### Example Outputs
metrics.json
```
[
  {
    "npi": "0000000000",
    "ndc": "00002323401",
    "fills": 82,
    "reverted": 4,
    "avg_price": 377.56,
    "total_price": 2509345.2
  },
  ...
]
```
drug_recommendation_by_chains.json
```
[
  {
    "ndc": "00015066812",
    "chain": [
      {
        "name": "health",
        "avg_price": 377.56
      },
      {
        "name": "saint",
        "avg_price": 413.40
      }
    ]
  },
  ...
]
```
most_prescribed_quantity_by_drug.json
```
[
  {
    "ndc": "00002323401",
    "most_prescribed_quantity": [8.5, 15.0, 45.0, ...]
  }
]
```

## Parallelization Performance Summary

28 claims files
4 reverts files
| Method          | Goal 2 Time | Goal 3 Time | Goal 4 Time | All         |
|-----------------|-------------|-------------|-------------|-------------|
| Normal          | 0.14s       | 0.15s       | 0.20s       | 0.27s       |
| Multiprocessing | 0.45s       | 0.53s       | 0.20s       | 0.84s       |

The multiprocessing code can be found in the branch [parallel_processing](https://github.com/GabrielCasemiro/Pharmacy-Data-Project/blob/parallel_processing/src/services/analytics_parallel.py).

We can notice the multiprocessing strategy was slower than normal processing. It happened because the overhead of parallelization outweighed the benefits in this particular scenario. As we have a Small Dataset, the overhead of creating new processes, transferring data between them, and collecting results can be more expensive than just processing the files sequentially. Parallelization often shows its strengths with larger workloads.