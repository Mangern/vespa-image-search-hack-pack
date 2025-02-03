# Feed a single image

```bash
./src/sh/feed-image.sh ./data/Flicker8k_Dataset/667626_18933d713e.jpg
```

# Feed precomputed embeddings

```bash
zstdcat flickr-8k-clip-embeddings.jsonl.zst | vespa feed -
```
