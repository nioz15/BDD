import os
import re
import time
import json
import requests
from pathlib import Path

# ---------------------------
# Configuration
# ---------------------------
venv_path = "/home/ubuntu/BDD/Dash/venv"
DOWNLOAD_DIR = "/home/ubuntu/BDD/Dash/static/downloaded-reports"
OS_ENDPOINT = "https://vpc-allure-os-ezoofboxprf2l2ag2xc7g7d6zm.us-east-1.es.amazonaws.com"
INDEX_NAME = "allure"
HEADERS = {"Content-Type": "application/json"}
SCROLL_TIMEOUT = "1m"  # Scroll timeout duration (keeps results active)
CUTOFF_SECONDS = 86400


def fetch_tags_last_1h():
    """
    Fetch all unique tags from the last 1 hour using the Scroll API.
    This bypasses the 10,000-document limit by paginating through results.
    """
    url = f"{OS_ENDPOINT}/{INDEX_NAME}/_search?scroll={SCROLL_TIMEOUT}"

    query_data = {
        "size": 1000,  # Batch size per scroll request
        "_source": ["properties.tag"],
        "sort": [{"time.start": {"order": "desc"}}],  # Sorting ensures recent results first
        "query": {
            "range": {
                "time.start": {
                    "gte": "now-1h",  #Fetch only the last 1 hour
                    "lte": "now"
                }
            }
        }
    }

    response = requests.post(url, headers=HEADERS, json=query_data)
    if response.status_code != 200:
        print(f"Failed to initiate scroll search. Status code: {response.status_code}")
        return []

    response_data = response.json()
    scroll_id = response_data.get("_scroll_id")
    if not scroll_id:
        print("No scroll_id returned, cannot continue.")
        return []

    hits = response_data["hits"]["hits"]
    tags = set()

    # Process first batch
    for hit in hits:
        tag = hit["_source"]["properties"]["tag"]
        tags.add(tag)

    # Continue scrolling through results
    scroll_url = f"{OS_ENDPOINT}/_search/scroll"
    while hits:
        scroll_payload = {"scroll_id": scroll_id, "scroll": SCROLL_TIMEOUT}
        scroll_response = requests.post(scroll_url, headers=HEADERS, json=scroll_payload)
        if scroll_response.status_code != 200:
            print(f"Failed during scrolling. Status code: {scroll_response.status_code}")
            break

        scroll_data = scroll_response.json()
        scroll_id = scroll_data.get("_scroll_id")
        hits = scroll_data["hits"]["hits"]

        for hit in hits:
            tag = hit["_source"]["properties"]["tag"]
            tags.add(tag)

    print(f"Fetched {len(tags)} unique tags from the last 1 hour.")
    return list(tags)


def extract_timestamp_from_filename(filename):
    """
    Extracts the timestamp from a filename of the format:
    mt-qa-1_c4_AUT-1825_1738408741.json
    Returns the timestamp as an integer or None if parsing fails.
    """
    match = re.search(r'_(\d+)\.json$', filename)
    return int(match.group(1)) if match else None


def get_existing_tags_with_timestamps(download_dir):
    """
    Scan the folder for existing JSON files and return a dictionary mapping
    tag -> timestamp extracted from filename.
    """
    existing_files = {}
    now = int(time.time())

    for file in Path(download_dir).glob("*.json"):
        timestamp = extract_timestamp_from_filename(file.name)
        if timestamp:
            tag = file.stem  # Keep the full tag name
            existing_files[tag] = timestamp

            # If file is older than 24 hours, mark for deletion
            if now - timestamp > CUTOFF_SECONDS:
                print(f"Deleting old file: {file.name}")
                file.unlink()

    return existing_files


def query_and_save_tags(tags, download_dir):
    """
    Query OpenSearch for each tag and save results, but only if it doesn't already exist.
    """
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    existing_tags = get_existing_tags_with_timestamps(download_dir)

    url = f"{OS_ENDPOINT}/{INDEX_NAME}/_search"

    for tag in tags:
        if tag in existing_tags:
            print(f"Skipping tag '{tag}' (already exists: {existing_tags[tag]}).")
            continue

        query_data = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"time.start": {"gte": "now-1h", "lte": "now"}}},  # Fetch last 1 hour only
                        {"match": {"properties.tag": tag}}
                    ]
                }
            }
        }

        response = requests.post(url, headers=HEADERS, json=query_data)
        if response.status_code == 200:
            filename = f"{tag}.json"  # No extra timestamp!
            output_file = os.path.join(download_dir, filename)
            with open(output_file, "w") as f:
                json.dump(response.json(), f, indent=4)
            print(f"Saved query result for tag '{tag}' to {filename}")
        else:
            print(f"Failed to fetch data for tag '{tag}'. Status code: {response.status_code}")


def main():
    """
    Main script flow:
    1) Fetch all unique tags using the Scroll API (last 1 hour only).
    2) Download data for missing tags only.
    3) Remove files older than 24 hour.
    """
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

    print("Fetching unique tags...")
    tags = fetch_tags_last_1h()

    print("Downloading new data...")
    query_and_save_tags(tags, DOWNLOAD_DIR)


if __name__ == "__main__":
    main()
