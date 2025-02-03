# Semantic Image Search - Python version

This Hack Pack includes a ready-to-use example of semantic image search using Vespa.

The application lets users search for images based on the **content** of the 
images - no additional metadata is used to retrieve search results.

There are two ways to use this hack pack

- [Locally using Docker](#setup---local-using-docker)
- [Vespa Cloud](#setup---vespa-cloud)

# Requirements
- [Vespa CLI](https://docs.vespa.ai/en/vespa-cli)
- [Python >= 3.11](https://www.python.org/downloads/release/python-3120/)
- [zstd](https://formulae.brew.sh/formula/zstd)

## Python dependencies

```bash
# Optional but recommended: virtual environment
python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
```

## Flicker8K dataset
The example is based on the Flicker8K dataset, which contains $8091$ images.
There is a script for downloading and extracting the dataset.
The total size after extraction is about $270$ MB.

```bash
cd dataset
./download_and_unzip.sh
cd ..
```

# Setup - local using Docker

The app can be hosted locally in a Docker container. 
PyVespa takes care of running the container and deploying the application.

```bash
vespa config set target local

cp .env-template-local .env

# Update .env to correct dataset path

python3 -m app.scripts.deploy_vespa
```

The python script will automatically start a docker container and deploy an application to it.

Next, follow the steps to [feed data and run the application frontend](#running-the-application)

# Setup - Vespa Cloud
Vespa Cloud is a simple way to host Vespa Applications on a cloud server.

To deploy the application to Vespa Cloud, first follow the [guide](https://cloud.vespa.ai/en/getting-started) 
to setup a tenant and make an application.

Configure the client
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
To actually do something useful we need to feed data.

Example images and embeddings from the Flicker8K dataset is included with a shell script:

```bash
cd dataset
./download_and_unzip_embeddings.sh

# Feed precomputed embeddings
zstdcat flicker8k_embeddings/vit_b_32/embeddings.jsonl.zst | vespa feed -

cd ..
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

## Cleanup after done
```bash
docker rm -f imagesearch
```
