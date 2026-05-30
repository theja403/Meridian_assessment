import os
from dotenv import load_dotenv
import requests
from pathlib import Path
import json


load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}


def get_all_datasets():
    page = 1
    all_records = []

    while True:
        print(f"Fetching page {page}...")

        response = requests.get(
            f"{BASE_URL}/api/v1/dataset",
            headers=HEADERS,
            params={"page": page},
            timeout=30,
        )
        print(response, response.status_code)
        response.raise_for_status()

        data = response.json()

        records = data.get("data", [])

        all_records.extend(records)

        print(
            f"Page={data.get('page')} "
            f"Records={len(records)} "
            f"Total Fetched={len(all_records)}"
        )

        if not data.get("has_more", False):
            break

        page += 1

    return all_records

def save_dataset(records):
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "dataset.json"

    with open(output_file, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Saved {len(records)} records to {output_file}")


if __name__ == "__main__":
    records = get_all_datasets()

    print(f"\nTotal Records Downloaded: {len(records)}")

    save_dataset(records)