FILENAME=$(basename $1)
BASE64=$(base64 -i data/Flicker8k_Dataset/$FILENAME)
curl -X POST \
    'http://localhost:8080/processing/?chain=image_embed_chain' \
    --header 'Content-Type: application/json' \
    --data '{"image_file_name": "'${FILENAME}'", "image": "'${BASE64}'" }'
