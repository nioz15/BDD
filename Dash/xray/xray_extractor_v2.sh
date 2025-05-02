#!/bin/bash

# Set input and output directories
INPUT_DIR="/home/ubuntu/BDD/Dash/xray"
OUTPUT_FILE="$INPUT_DIR/all_features.txt"

# Download and process the BDD features
TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id XrayToken \
  --region us-east-1 \
  --query SecretString \
  --output text | jq -r '.Token')

if [ -z "$TOKEN" ]; then
  echo "Failed to retrieve TOKEN from AWS Secrets Manager."
  exit 1
fi

FILTER_ID="17917"
API_URL="https://xray.cloud.getxray.app/api/v2/export/cucumber?filter=$FILTER_ID"
ZIP_FILE="$INPUT_DIR/zipfile.zip"
EXTRACTED_DIR="$INPUT_DIR/extracted_features"

# Fetch features and unzip
curl --retry 5 --retry-all-errors --retry-max-time 120 \
  --location "$API_URL" \
  --header "Accept: application/json" \
  --header "Authorization: Bearer $TOKEN" \
  --output "$ZIP_FILE"

mkdir -p "$EXTRACTED_DIR"
unzip -o "$ZIP_FILE" -d "$EXTRACTED_DIR" >/dev/null 2>&1

# Combine features into the output file
rm -f "$OUTPUT_FILE"
for feature_file in "$EXTRACTED_DIR"/*.feature; do
  if [ -f "$feature_file" ]; then
    in_examples_block=false
    while IFS= read -r line; do
      clean_line=$(echo "$line" | sed 's/^\s*//')
      if [[ "$clean_line" =~ ^Examples ]]; then
        echo "$clean_line" >> "$OUTPUT_FILE"
        in_examples_block=true
      elif $in_examples_block && [[ "$clean_line" =~ ^\| ]]; then
        echo "$clean_line" >> "$OUTPUT_FILE"
      else
        in_examples_block=false
        if [[ "$clean_line" =~ ^(Given|When|Then|And) ]]; then
          echo "$clean_line" >> "$OUTPUT_FILE"
        fi
      fi
    done < "$feature_file"
    echo "#" >> "$OUTPUT_FILE"
  fi
done
