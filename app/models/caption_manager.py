from pathlib import Path
from typing import Dict, Optional


class CaptionManager:
    """Manages captions for images."""

    _instance = None
    _initialized = False
    _captions: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._load_captions()

    def _load_captions(self) -> None:
        """Load captions from the summarized dataset file."""
        captions_path = Path("dataset/flickr8k/captions_summarized.txt")
        if not captions_path.exists():
            print(f"Warning: Captions file not found at {captions_path}")
            return

        try:
            with open(captions_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        # Split on first comma only since caption might contain commas
                        image_name, caption = line.strip().split(",", 1)
                        # Clean up whitespace
                        image_name = image_name.strip()
                        caption = self._clean_caption(caption)
                        self._captions[image_name] = caption
                    except ValueError:
                        continue  # Skip malformed lines

            print(f"Loaded captions for {len(self._captions)} images")
        except Exception as e:
            print(f"Error loading captions: {e}")

    @staticmethod
    def _clean_caption(caption: str) -> str:
        """Clean caption text by removing extra whitespace."""
        return caption.strip()

    def get_caption(self, image_name: str) -> Optional[str]:
        """Get the caption for the given image."""
        return self._captions.get(image_name)
