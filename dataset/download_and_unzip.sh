#!/bin/bash

# Define the URL and the output filename
URL="https://data.vespa-cloud.com/sample-apps-data/flickr8k.zip"
OUTPUT_FILE="flickr8k.zip"

# Download the file
echo "Downloading $URL..."
curl -O $URL

# Check if the file was downloaded successfully
if [ -f "$OUTPUT_FILE" ]; then
  echo "Download completed successfully. Extracting $OUTPUT_FILE..."

  # Unzip the file
  unzip "$OUTPUT_FILE" && rm "$OUTPUT_FILE"

  # Check if the unzip was successful
  if [ $? -eq 0 ]; then
    echo "Extraction completed successfully."

    # Remove the __MACOSX folder if it exists
    if [ -d "__MACOSX" ]; then
      echo "Removing __MACOSX folder..."
      rm -rf __MACOSX
      echo "__MACOSX folder removed."
    fi

    # Remove any `._*` files
    echo "Removing any resource fork files (._*)..."
    find . -name "._*" -exec rm -f {} \;
    echo "Resource fork files removed."
  else
    echo "Failed to extract the file."
  fi
else
  echo "Failed to download the file."
fi
