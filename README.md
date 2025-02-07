# Semantic Image Search - Python version

This Hack Pack includes a ready-to-use example of semantic image search using Vespa.

The application lets users search for images based on the **content** of the 
images - no additional metadata is used to retrieve search results.

There are two ways to use this hack pack

- [Locally using Docker](#setup---local-using-docker)
- [Vespa Cloud](#setup---vespa-cloud)

Using Docker means you host a Vespa instance locally on your own machine.

Using Vespa Cloud is a good way to quickly deploy a Vespa application to the cloud, and not worry about hosting details.

# Requirements
- [Vespa CLI](https://docs.vespa.ai/en/vespa-cli)
- [Python >= 3.11](https://www.python.org/downloads/release/python-3120/)
- [zstd](https://formulae.brew.sh/formula/zstd)
- [git-lfs](https://git-lfs.com/) for pulling the dataset

## Download repository

```bash
git clone -b penne-pixels https://github.com/Mangern/vespa-image-search-hack-pack.git
cd vespa-image-search-hack-pack
git lfs pull
```

## Python dependencies

```bash
# Optional but recommended: virtual environment
python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
```

# Setup - locally using Docker

This section describes how to setup the application for hosting locally in a container.

The app can be hosted locally in a Docker container. 
PyVespa takes care of running the container and deploying the application.

```bash
vespa config set target local

cp .env-template-local .env

python3 -m app.scripts.deploy_vespa
```

The python script will automatically start a container and deploy an application to it.

Next, follow the steps to [feed data and run the application frontend](#running-the-application)

# Setup - Vespa Cloud
Vespa Cloud is a simple way to host Vespa Applications on a cloud server.

To deploy the application to Vespa Cloud, first head over to [Vespa Cloud](https://console.vespa-cloud.com/), sign up and [create a tenant](https://cloud.vespa.ai/en/getting-started).

Next, configure the Vespa client:
```bash
vespa config set target cloud

vespa auth login
vespa auth cert

cp .env-template-cloud .env

# Update .env variables:
# - VESPA_TENANT
# - VESPA_APPLICATION
# - VESPA_INSTANCE
# - VESPA_CERTIFICATE
# - VESPA_PRIVATE_KEY
# Endpoint and API key can be set later

python3 -m app.scripts.deploy_vespa
```

If everything was successful, you should get an output like:

```bash
INFO    [12:16:34]  Deployment of new application complete!
Only region: aws-us-east-1c available in dev environment.
Found mtls endpoint for imagesearch_container
URL: https://xxxxxxxx.xxxxxxxx.z.vespa-app.cloud/
Application is up!
2025-02-03 13:16:37,647 - vespa_search - INFO - Deployment initiated successfully
2025-02-03 13:16:37,648 - vespa_search - INFO - Deployment completed successfully
```

Update `VESPA_ENDPOINT` in `.env` with the resulting endpoint.

# Running the application

## Feeding data
To actually do something useful we need to feed data to Vespa.

The example is based on the Flicker8K dataset, which contains $8091$ images.
There is a script for downloading and extracting the dataset.
The total size after extraction is about $350$ MB.


Example images and embeddings from the Flicker8K dataset is included with a shell script:

```bash
# Extract dataset
./sh/extract-dataset.sh

# Feed precomputed embeddings
zstdcat dataset/flickr8k/embeddings-vit-b-32.jsonl.zst | vespa feed -
```

If everything was successful you should get an output like this:

```json
{
  "feeder.operation.count": 8091,
  ...
  "http.response.code.counts": {
    "200": 8091
  }
}
```

This means that $8091$ documents were successfully fed to the application.

## Run the frontend server
```bash
python3 dev_server.py
```

Try to search for something:)

## Cleanup after done (if local)
```bash
docker rm -f imagesearch
```
