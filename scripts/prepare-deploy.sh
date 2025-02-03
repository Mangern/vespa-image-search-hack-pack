#!/bin/sh

# Extract dataset
if ! test -d dataset/flickr8k; then
    echo "Extracting dataset"
    cd dataset
    tar xvf flickr8k.tgz
    cd ..
fi

# Export CLIP models in ONNX format
if ! test -f src/main/application/models/visual.onnx -a -f src/main/application/models/transformer.onnx; then
    echo "Exporting onnx models"
    mkdir -p src/main/application/models/
    ./scripts/clip_export.py ViT-B/32 src/main/application/models/
fi
