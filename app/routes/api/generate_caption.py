import json
from pathlib import Path

from fasthtml.common import Response

from ...models.caption_manager import CaptionManager


def register_routes(rt):
    """Register the caption generation routes."""

    caption_manager = CaptionManager()

    @rt("/api/generate-caption")
    async def generate_caption(req):
        """Get a caption for the specified image."""
        try:
            image_path = req.query_params.get("image")
            if not image_path:
                return Response(
                    json.dumps({"error": "No image path provided"}),
                    media_type="application/json",
                    status_code=400,
                )

            image_name = Path(image_path).name
            caption = caption_manager.get_caption(image_name)

            if not caption:
                return Response(
                    json.dumps({"error": f"No caption found for image: {image_name}"}),
                    media_type="application/json",
                    status_code=404,
                )

            return Response(
                json.dumps({"caption": caption}), media_type="application/json"
            )

        except Exception as e:
            print(f"Error in caption endpoint: {e}")
            return Response(
                json.dumps({"error": str(e)}),
                media_type="application/json",
                status_code=500,
            )
