import sys
import os
import requests
import json
from pathlib import Path

# Path to the virtual environment (if necessary)
venv_path = "/home/ubuntu/BDD/Dash/venv"

# Function to perform the initial search query and extract unique tags
def fetch_tags(size):
    url = "https://vpc-allure-os-ezoofboxprf2l2ag2xc7g7d6zm.us-east-1.es.amazonaws.com/allure/_search"
    headers = {'Content-Type': 'application/json'}
    query_data = {
        "size": size,
        "_source": ["properties.tag"],
        "sort": [{"time.start": {"order": "desc"}}]
    }

    # Perform the search query
    response = requests.get(url, headers=headers, json=query_data)
    tags = set()  # Using a set to store unique tags

    # Check if the response is successful
    if response.status_code == 200:
        response_data = response.json()

        # Extract tags from the hits
        for hit in response_data['hits']['hits']:
            tag = hit['_source']['properties']['tag']
            tags.add(tag)  # Add tags to the set (duplicates are automatically handled)
        print(f"Fetched {len(tags)} unique tags.")
    else:
        print(f"Failed to fetch tags. Status code: {response.status_code}")
    
    return list(tags)  # Convert set back to list for further processing

# Function to clean all files in the download directory
def clean_download_directory(download_dir):
    # Ensure the download directory exists
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    # Clean all files in the download directory
    for file_path in Path(download_dir).glob("*"):  # This will match all files
        if file_path.is_file():
            file_path.unlink()  # Delete the file
    print(f"Cleaned all files in {download_dir}")

# Function to query based on the tags and save the responses
def query_by_tag_and_save(tags, download_dir):
    # Ensure the download directory exists
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    # OpenSearch endpoint and headers
    url = "https://vpc-allure-os-ezoofboxprf2l2ag2xc7g7d6zm.us-east-1.es.amazonaws.com/allure/_search"
    headers = {'Content-Type': 'application/json'}

    # Iterate through the unique tags and perform queries
    for tag in tags:
        # Define the query for the specific tag
        query_data = {
            "query": {
                "match": {
                    "properties.tag": tag
                }
            }
        }

        # Perform the OpenSearch query
        response = requests.post(url, headers=headers, json=query_data)

        # Save the response to a file named after the tag
        output_file = os.path.join(download_dir, f"{tag}.json")
        if response.status_code == 200:
            with open(output_file, "w") as f:
                json.dump(response.json(), f, indent=4)
            print(f"Saved query result for tag '{tag}' to {output_file}")
        else:
            print(f"Failed to fetch data for tag '{tag}'. Status code: {response.status_code}")

# Main function to run the complete workflow
def main():
    # Path to the virtual environment and download directory
    download_dir = "/home/ubuntu/BDD/Dash/static/downloaded-reports"

    # Number of unique tags you want to fetch
    size = 10000  # Change this to the desired number of unique tags

    # Clean the download directory before processing
    clean_download_directory(download_dir)

    # Step 1: Fetch unique tags from the first query (limit by size)
    tags = fetch_tags(size)

    # Step 2: Query based on the fetched tags and save the results
    query_by_tag_and_save(tags, download_dir)

if __name__ == "__main__":
    main()
