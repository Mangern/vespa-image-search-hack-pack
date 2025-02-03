# Semantic Image Search - Java version

This Hack Pack features a ready-to-use example of semantic image search using Vespa.

The application lets users search for images based on the **content** - no additional metadata is used for retrieving search results.

Vespa supports writing custom Java components, which is the most powerful and flexible method of
creating a custom API on top of Vespa.

## Features
- Search images from the Flicker8K dataset semantically. Receive suggestions for what to search when clicking an image.
- Approximate nearest neighbor retrieval based on CLIP embeddings.
- Java Searcher component for embedding user text queries entirely within Vespa.
- Java Processor component for feeding images and computing embeddings directly.

# Requirements
- [Java 17](https://openjdk.org/projects/jdk/17/) to build the Java components.
- [Vespa CLI](https://docs.vespa.ai/en/vespa-cli.html) to deploy the application and feed data.
- [Python 3.12](https://www.python.org/downloads/) to export CLIP models and host the Web frontend.
- [zstd](https://formulae.brew.sh/formula/zstd) to feed precomputed embeddings.
- [Docker](https://www.docker.com/) or [Podman](https://podman.io/) to host Vespa locally.

## Quickstart

### Requires internet connection

```bash
git clone -b java https://github.com/Mangern/vespa-image-search-hack-pack.git && cd vespa-image-search-hack-pack
git lfs pull

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

mvn -U package
```

If all the commands were successful, everything needed to run this sample should be downloaded.

### Run local Vespa instance
```bash
vespa config set target local
docker run --detach --name vespa --hostname vespa-container \
  --publish 127.0.0.1:8080:8080 --publish 127.0.0.1:19071:19071 vespaengine/vespa
```

### Deploy Vespa application
```bash
# Assumes mvn package has been run successfully in the workspace

vespa status deploy --wait 300
vespa deploy --wait 300
```

### Run web app
```bash
python3 dev_server.py
```

## Feeding data

After deploying and running the application, searching will give 0 results.

This is because the data has to be **fed** to the running Vespa instance. This includes image file names and embeddings.

### Feed precomputed embeddings

The easiest way to feed data to a Vespa application is by using `vespa feed` from the CLI.
Feel free to look at the embeddings file to see the required data format.

```bash
zstdcat ./dataset/flickr8k/embeddings-vit-b-32.jsonl.zst | vespa feed -
```

### Feeding a single image

The hack pack features feeding images directly through a custom Processor chain.

The [scripts/feed-image.sh](./scripts/feed-image.sh) script simply Base64-encodes an image and sends it to the processor.

```bash
./scripts/feed-image.sh ./dataset/flickr8k/667626_18933d713e.jpg
```

The code in [src/main/java/ai/vespa/example/ImageEmbeddingProcessor.java](./src/main/java/ai/vespa/example/ImageEmbeddingProcessor.java)
shows what happens when an image is fed this way.

## Next steps

Try to feed your own data by using the provided shell script.

Interesting files to explore and modify:

- [src/main/application/schemas/image_search.sd](./src/main/application/schemas/image_search.sd) - This is where the document type for storing, indexing and querying embeddings is defined.
- [src/main/java/ai/vespa/example/ImageEmbeddingProcessor.java](./src/main/java/ai/vespa/example/ImageEmbeddingProcessor.java) - 
This is where computation of embeddings when feeding happens.
- [src/main/java/ai/vespa/example/TextEmbeddingSearcher.java](./src/main/java/ai/vespa/example/TextEmbeddingSearcher.java) - 
This is a custom Vespa Searcher that creates an embedding of the user supplied text query and uses it to perform a nearest neighbor query 
on the indexed image embeddings.
- [app/](./app/) - Contains all the front-end code.
