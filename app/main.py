import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import uvicorn
from dotenv import load_dotenv
from fasthtml.common import Link, Meta, Script, StaticFiles, fast_app

from app.models.caption_manager import CaptionManager

from .routes import register_routes

# Load environment variables from .env file
load_dotenv()

# Define paths - both relative to project root
STATIC_DIR = Path(__file__).parent / "static"

DATASET_DIR = Path(
    os.getenv("DATASET", "dataset")
)  # Default to 'dataset' in project root

# Validate dataset directory and captions file
if not DATASET_DIR.exists() or not DATASET_DIR.is_dir():
    raise RuntimeError(
        f"Dataset directory not found at {DATASET_DIR}. "
        "Please check your DATASET environment variable."
    )

captions_file = DATASET_DIR / "flickr8k/captions.txt"
if not captions_file.exists():
    raise RuntimeError(
        f"Captions file not found at {captions_file}. "
        "Please ensure the Flickr8k dataset is properly set up."
    )


@dataclass
class Dependency:
    """Represents an external dependency (JS/CSS) with its configuration."""

    js: Optional[str] = None
    css: Optional[str] = None
    init: Optional[str] = None
    description: str = ""
    attributes: dict = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

    def to_ft(self) -> List[Union[Script, Link]]:
        """Convert dependency to FastHTML FT components."""
        components = []

        # Add CSS if specified
        if self.css:
            components.append(Link(rel="stylesheet", href=self.css))

        # Add JavaScript if specified
        if self.js:
            script_attrs = {"src": self.js, **self.attributes}
            components.append(Script(**script_attrs))

        # Add initialization script if specified
        if self.init:
            components.append(Script(src=self.init))

        return components


# Application dependencies
DEPENDENCIES = [
    Dependency(
        js="/app/static/js/theme-init.js",
        description="Theme initialization",
    ),
    Dependency(
        js="/app/static/js/theme.js",
        description="Theme management system",
        attributes={"defer": True},
    ),
    Dependency(
        js="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js",
        description="HTMX SSE extension for real-time updates",
    ),
    Dependency(
        js="https://kit.fontawesome.com/bd81a17e1a.js",
        description="Font Awesome icons",
        attributes={"crossorigin": "anonymous"},
    ),
    Dependency(
        css="/app/static/css/theme-init.css", description="Theme transitions styles"
    ),
    Dependency(css="/app/static/css/output.css", description="TailwindCSS styles"),
]


def get_font_headers() -> tuple:
    """Generate font loading headers."""
    return (
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=True),
        Link(
            href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
            rel="stylesheet",
        ),
    )


def get_favicon_headers() -> tuple:
    """Generate favicon and related meta headers."""
    return (
        # Basic favicons
        Link(
            rel="icon",
            type="image/png",
            sizes="32x32",
            href="/app/static/favicon/favicon-32x32.png",
        ),
        Link(
            rel="icon",
            type="image/png",
            sizes="16x16",
            href="/app/static/favicon/favicon-16x16.png",
        ),
        Link(rel="shortcut icon", href="/app/static/favicon/favicon.ico"),
        # Apple Touch Icon
        Link(
            rel="apple-touch-icon",
            sizes="180x180",
            href="/app/static/favicon/apple-touch-icon.png",
        ),
        # Safari Pinned Tab
        Link(
            rel="mask-icon",
            href="/app/static/favicon/safari-pinned-tab.svg",
            color="#61d790",
        ),
        # Web Manifest
        Link(rel="manifest", href="/app/static/favicon/site.webmanifest"),
        # Microsoft Tile Color
        Meta(name="msapplication-TileColor", content="#2e2f27"),
        Meta(
            name="msapplication-config", content="/app/static/favicon/browserconfig.xml"
        ),
        # Theme Color
        Meta(name="theme-color", content="#2e2f27"),
    )


def get_mobile_meta_headers() -> tuple:
    """Generate mobile-related meta headers."""
    return (
        Meta(
            name="viewport",
            content="width=device-width, initial-scale=1.0, viewport-fit=cover",
        ),
        Meta(name="mobile-web-app-capable", content="yes"),
        Meta(name="apple-mobile-web-app-status-bar-style", content="black"),
    )


def load_dependencies() -> tuple:
    """Convert all dependencies to FT components."""
    components = []
    for dep in DEPENDENCIES:
        components.extend(dep.to_ft())
    return tuple(components)


# Initialize FastHTML application
app, rt = fast_app(
    pico=False,
    hdrs=(
        *load_dependencies(),
        *get_favicon_headers(),
        *get_font_headers(),
        *get_mobile_meta_headers(),
    ),
    htmlkw={"cls": "grid h-dvh"},
)


@app.on_event("startup")
async def startup_event():
    """Initialize application components."""
    print("Starting application initialization...")
    CaptionManager()  # Initialize the singleton
    print("Application initialization complete!")


# Mount static files directories
app.mount("/app/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/dataset", StaticFiles(directory=str(DATASET_DIR)), name="dataset")

# Register all routes
register_routes(rt)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        timeout_keep_alive=0,
        timeout_graceful_shutdown=1,
    )
