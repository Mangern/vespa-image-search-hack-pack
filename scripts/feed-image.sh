#!/bin/bash

JSON_ARRAY="["

# Loop through all provided image files
for IMAGE in "$@"; do
    FILENAME=$(basename "$IMAGE")
    BASE64=$(base64 -i "$IMAGE")
    
    JSON_ARRAY+="{\"image_file_name\": \"${FILENAME}\", \"image\": \"${BASE64}\"},"
done

JSON_ARRAY=${JSON_ARRAY%,}]

# Send the request
curl -X POST \
    'http://localhost:8080/processing/?chain=image_embed_chain' \
    --header 'Content-Type: application/json' \
    --data "$JSON_ARRAY"
