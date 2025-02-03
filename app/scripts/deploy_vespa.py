#!/usr/bin/env python3
"""
Deploy Vespa Application Script.
This script initializes and deploys a Vespa application with CLIP model configurations.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional

import clip
import torch
from vespa.package import ApplicationPackage

from ..services.vespa.core.vespa_service import VespaService
from ..services.vespa.services.clip_service import ClipService
from ..services.vespa.utils.exceptions import VespaSearchError
from ..services.vespa.utils.logger import Logger

logger = Logger.get_logger()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy Vespa Application")
    parser.add_argument(
        "--model-name",
        type=str,
        default="ViT-B/32",
        help="CLIP model name (default: ViT-B/32)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to load CLIP model on",
    )
    parser.add_argument(
        "--instance",
        type=str,
        help="Optional instance name for deployment",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print application package without deploying",
    )
    return parser.parse_args()


def get_model_specs(model_name: str, device: str) -> Dict[str, int]:
    """
    Get model specifications using CLIP model.

    Args:
        model_name: Name of the CLIP model
        device: Device to load model on ('cpu' or 'cuda')

    Returns:
        Dictionary mapping model name to embedding size
    """
    try:
        # Load CLIP model
        model, _ = clip.load(model_name, device=device)

        # Get embedding size using dummy encoding
        with torch.no_grad():
            dummy_text = clip.tokenize(["test"])
            dummy_features = model.encode_text(dummy_text)
            embedding_size = dummy_features.shape[1]

        logger.info(f"Model {model_name} loaded with embedding size {embedding_size}")
        return {model_name: embedding_size}

    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
        sys.exit(1)


def print_application_info(app_package: ApplicationPackage) -> None:
    """
    Print the application package configuration using built-in text methods.

    Args:
        app_package: The initialized ApplicationPackage
    """
    print("\nApplication Package Configuration")
    print("=" * 35)

    print("\nSchema Configuration:")
    print("-" * 20)
    print(app_package.schema.schema_to_text)

    print("\nServices Configuration (services.xml):")
    print("-" * 35)
    print(app_package.services_to_text)


def deploy_application(
    clip_service: ClipService, instance: Optional[str] = None, dry_run: bool = False
) -> None:
    """
    Initialize and deploy Vespa application.

    Args:
        clip_service: Initialized ClipService instance
        instance: Optional instance name for deployment
        dry_run: If True, only print application package without deploying
    """
    try:
        # Get model specs from the ClipService
        model_specs = {clip_service.model_name: clip_service.embedding_size}

        # Initialize Vespa service
        vespa_service = VespaService()

        # Initialize application package
        logger.info("Initializing application package...")
        app_package: ApplicationPackage = vespa_service.initialize_application(model_embedding_specs=model_specs)

        if dry_run:
            logger.info("Dry run - printing application package details:")
            print_application_info(app_package)

            # Still save the files for reference
            output_dir = Path("temp_deploy")
            app_package.to_files(output_dir)
            logger.info(f"Application package files saved to: {output_dir}")
            return

        # Deploy application
        logger.info(
            f"Deploying application{f' to instance {instance}' if instance else ''}..."
        )
        vespa_service.deploy_application(app_package, instance)
        logger.info("Deployment completed successfully")

    except VespaSearchError as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        sys.exit(1)


def main() -> None:
    args = parse_args()

    try:
        # Initialize CLIP service
        logger.info(f"Initializing CLIP service with model {args.model_name}")
        clip_service = ClipService(model_name=args.model_name, device=args.device)

        logger.info(f"Deploying application with CLIP model: {args.model_name}")
        deploy_application(
            clip_service=clip_service, instance=args.instance, dry_run=args.dry_run
        )

    except Exception as e:
        logger.error(f"Deployment script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
