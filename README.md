# Run local Vespa instance
```bash
vespa config set target local
docker run --detach --name vespa --hostname vespa-container \
  --publish 127.0.0.1:8080:8080 --publish 127.0.0.1:19071:19071 vespaengine/vespa
```

# Build and deploy
```bash
mvn -U clean package
vespa status deploy --wait 300
vespa deploy --wait 300
```

# Run web app
```bash
cd src/webapp
npm run dev
```

# Feeding a single image

```bash
./src/sh/feed-image.sh ./data/Flicker8k_Dataset/667626_18933d713e.jpg
```

# Feed precomputed embeddings

```bash
zstdcat flickr-8k-clip-embeddings.jsonl.zst | vespa feed -
```
