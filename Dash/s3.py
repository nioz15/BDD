import os
import sys

venv_path = "/home/ubuntu/BDD/Dash/venv"

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Define variables
S3_BUCKET = "avanan-automation-allure-dev"
DOWNLOAD_DIR = "/home/ubuntu/BDD/Dash/static/downloaded-reports"

# Create a session and S3 client
session = boto3.Session()
s3 = session.client('s3')

# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Ensure the HTML file name is provided as a parameter
if len(sys.argv) < 2:
    print("Error: Please provide an HTML file name as a parameter.")
    sys.exit(1)

html_file_name = sys.argv[1]
print(f"Downloading file: {html_file_name}")

# Define the S3 key (assuming the file is in a folder like 'qa', 'cp', or 'av')
directories = ["qa", "cp", "av"]
found_file = False

# Clean any existing HTML file in the download directory with the same name
for file_name in os.listdir(DOWNLOAD_DIR):
    if file_name == html_file_name:
        os.remove(os.path.join(DOWNLOAD_DIR, file_name))
        print(f"Deleted existing file: {file_name}")

# Try to find and download the file from the given directories
for dir in directories:
    s3_key = f"{dir}/{html_file_name}"
    try:
        # Check if the file exists in this directory
        s3.head_object(Bucket=S3_BUCKET, Key=s3_key)

        # File exists, proceed with download
        s3.download_file(S3_BUCKET, s3_key, os.path.join(DOWNLOAD_DIR, html_file_name))
        print(f"Downloaded {html_file_name} from {dir} directory.")
        found_file = True
        break

    except ClientError as e:
        # Check if the error is because the file doesn't exist
        if e.response['Error']['Code'] == '404':
            print(f"File {html_file_name} not found in {dir} directory.")
        else:
            print(f"Error checking file {html_file_name}: {e}")

if not found_file:
    print(f"Error: {html_file_name} not found in any directory.")
