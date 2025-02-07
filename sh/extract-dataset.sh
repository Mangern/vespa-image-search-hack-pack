#!/bin/sh
# Extract dataset
if ! test -d dataset/flickr8k; then
    echo "Extracting dataset"
    cd dataset
    tar xvf flickr8k.tgz
    cd ..
fi
