from typing import Dict, Iterable
from vespa.application import Vespa
from vespa.io import VespaResponse
from app.services.vespa.config.schema_config import SchemaConfig
from app.services.vespa.core.model_registry import ModelRegistry
from ..services.vespa.utils.logger import Logger
from ..services.vespa.config.app_config import AppConfig
from ..services.vespa.infrastructure.vespa_client import VespaClient
import clip
import torch
import ntpath
import glob, os
from tenacity import retry, wait_exponential, stop_after_attempt
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

logger = Logger.get_logger()

class ImageFeedDataset(Dataset):
    def __init__(self, img_dir, model_name):
        """
        PyTorch Dataset to compute image embeddings and return pyvespa-compatible feed data.

        :param img_dir: Folder containing image files.
        :param model_name: CLIP model name.
        """
        valid_vespa_model_name = ModelRegistry.normalize_model_name(model_name)

        self.model, self.preprocess = clip.load(model_name)
        self.img_dir = img_dir
        self.image_file_names = glob.glob(os.path.join(img_dir, "*.jpg"))
        self.image_embedding_name = valid_vespa_model_name + "_image"

    def _from_image_to_vector(self, x):
        """
        From image to embedding.

        :param x: PIL images
        :return: normalized image embeddings.
        """
        with torch.no_grad():
            image_features = self.model.encode_image(
                self.preprocess(x).unsqueeze(0)
            ).float()
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features

    def __len__(self):
        return len(self.image_file_names)

    def __getitem__(self, idx):
        image_file_name = self.image_file_names[idx]
        image = Image.open(image_file_name)
        image = self._from_image_to_vector(image)
        image_base_name = ntpath.basename(image_file_name)
        return {
            "id": image_base_name.split(".jpg")[0],
            "fields": {
                "image_file_name": image_base_name,
                self.image_embedding_name: {"values": image.tolist()[0]},
            },
            "create": True,
        }

@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(3))
def feed_embeddings(app: Vespa, batch: Iterable[Dict], schema: str):
    def callback(response: VespaResponse, id):
        if not response.is_successful():
            print(f"Error when feeding document {id}: {response.get_json()}")

    app.feed_iterable(iter=batch, schema=schema, callback=callback)


def main():
    """
    Script to illustrate feeding with PyVespa.
    """
    config = AppConfig.get_instance()
    model_name = os.getenv("SPECIFIC_MODEL", "ViT-B/32")
    image_dir  = os.path.join(os.getenv("DATASET", "dataset"), "flickr8k")
    image_dataset = ImageFeedDataset(image_dir, model_name)
    dataloader = DataLoader(
        image_dataset,
        batch_size=128,
        shuffle=False,
        collate_fn=lambda x: x
    )
    client = VespaClient()
    # Access the underlying Vespa object for clarity
    app = client.vespa_app

    for idx, batch in enumerate(tqdm(dataloader)):
        feed_embeddings(app, batch, SchemaConfig.schema_name)


if __name__ == "__main__":
    exit(main())
