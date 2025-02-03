import math
import random
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from fasthtml.common import Div, Img, Input, Script, Style

GRID_PARAMS: Set[str] = {"cls", "min_cols", "gap", "min_cell_size", "content_attrs"}

GRID_STYLES = """
.grid-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100dvw;
    height: 100dvh;
    min-height: 100dvh;
    z-index: 0;
    overflow: hidden;
    background: color-mix(in srgb, var(--app-background) 20%, transparent);

    /* Grid setup with dynamic sizing */
    display: grid;
    grid-template-columns: repeat(var(--column-count), var(--cell-size));
    grid-template-rows: repeat(var(--row-count), var(--cell-size));
    grid-auto-flow: row dense;
    gap: var(--grid-gap, 5px);

    /* Center the grid */
    justify-content: center;
    align-content: center;

    /* Transform for performance */
    transform: translateZ(0);

    /* Fibonacci-inspired gradients (approximately 89%/78%/61.8%) */
    mask-image:
        radial-gradient(
            ellipse at center,
            black 89%,
            transparent 100%
        ),
        radial-gradient(
            circle at center,
            black 78%,
            transparent 100%
        );
    -webkit-mask-image:
        radial-gradient(
            ellipse at center,
            black 89%,
            transparent 100%
        ),
        radial-gradient(
            circle at center,
            black 78%,
            transparent 100%
        );
    mask-composite: intersect;
    -webkit-mask-composite: source-in;

    /* Subtler vignette overlay using golden ratio-inspired stops */
    &::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(
            circle at center,
            transparent 61.8%,
            transparent 89%,
            var(--app-background) 100%
        );
        opacity: 0.4; /* Reduced from 0.6 */
        pointer-events: none;
        z-index: 2;
    }

    /* More subtle corner reinforcement */
    &::after {
        content: '';
        position: absolute;
        inset: 0;
        background:
            radial-gradient(circle at 0 0, var(--app-background) 0%, transparent 21%),
            radial-gradient(circle at 100% 0, var(--app-background) 0%, transparent 21%),
            radial-gradient(circle at 0 100%, var(--app-background) 0%, transparent 21%),
            radial-gradient(circle at 100% 100%, var(--app-background) 0%, transparent 21%);
        opacity: 0.3; /* Reduced from 0.4 */
        pointer-events: none;
        z-index: 2;
    }
}

/* Content overlay with pointer-events handling */
.grid-content {
    position: relative;
    z-index: 1;
    width: 100%;
    min-height: 100vh;
    pointer-events: none;  /* Let events pass through to grid */
}

/* But enable pointer events for actual content */
.grid-content > * {
    pointer-events: auto;  /* Re-enable events for content children */
}

.grid-cell {
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    width: var(--cell-size);
    height: var(--cell-size);
    contain: content;
    cursor: pointer;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced skeleton loading effect */
.grid-cell-skeleton {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        110deg,
        var(--subtle-background) 0%,
        var(--ui-element-background) 40%,
        var(--subtle-background) 80%
    );
    background-size: 200% 100%;
    animation: skeleton-loading 1s ease infinite;
    opacity: 0.7;
}

.grid-cell-image {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: grayscale(0.9);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0;
    transform-origin: center center;
    will-change: transform, opacity, filter;
}

/* Use a more specific selector to control loaded state opacity */
.grid-cell .grid-cell-image.loaded {
    opacity: 0.3;
}

/* Individual cell dimming */
.grid-cell::after {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--app-background);
    opacity: 0.35;
    transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}

/* Hover effects */
.grid-cell:hover .grid-cell-image {
    filter: grayscale(0) brightness(1.1) saturate(1.2) contrast(1.05);
    transform: scale(1.1);
    opacity: 1;  /* Full opacity on hover */
}

.grid-cell:hover::after {
    opacity: 0;
}

/* Neighbor hover effect */
.grid-cell.neighbor-hover {
    .grid-cell-image {
        filter: grayscale(0.4);
        transform: scale(1.05);
        opacity: 0.6;  /* Partial opacity for neighbors */
    }
    &::after {
        opacity: 0.2;
    }
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.grid-cell.processing {
    cursor: wait;
    position: relative;
}

.grid-cell.processing::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--app-background);
    opacity: 0.7;
    z-index: 3;
}

.grid-cell.processing::after {
    content: '';
    position: absolute;
    width: 24px;
    height: 24px;
    top: 50%;
    left: 50%;
    margin: -12px 0 0 -12px;
    border: 2px solid transparent;
    border-top-color: var(--solid-background);
    border-radius: 50%;
    animation: cell-spinner 0.8s linear infinite;
    z-index: 4;
}

@keyframes cell-spinner {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Optimize for reduced motion */
@media (prefers-reduced-motion: reduce) {
    .grid-cell-image {
        transition: opacity 0.1s linear !important;
    }
    .grid-cell:hover .grid-cell-image {
        transform: none !important;
    }
}
"""

VIEWPORT_SCRIPT = """
(() => {
    let resizeTimer;
    let lastDims = {width: 0, height: 0};

    function getViewportDimensions() {
        return {
            width: Math.floor(window.innerWidth || document.documentElement.clientWidth),
            height: Math.floor(window.innerHeight || document.documentElement.clientHeight),
        };
    }

    function updateViewport(triggerHTMX = true) {
        try {
            const {width, height} = getViewportDimensions();

            if (width === lastDims.width && height === lastDims.height) {
                return;
            }

            lastDims = {width, height};

            const widthInput = document.getElementById('viewport-width');
            const heightInput = document.getElementById('viewport-height');

            if (!widthInput || !heightInput) {
                console.error('Viewport inputs not found. Grid resizing may not work as expected.');
                return;
            }

            widthInput.value = width;
            heightInput.value = height;

            if (triggerHTMX) {
                const grid = document.querySelector('.grid-background');
                if (grid) {
                    requestAnimationFrame(() => {
                        htmx.trigger(grid, 'size-update');
                    });
                }
            }
        } catch (error) {
            console.error('Error updating viewport:', error);
        }
    }

    // Ensure updates on initial load
    document.addEventListener('DOMContentLoaded', () => {
        updateViewport(true);
    });
    window.addEventListener('load', () => {
        updateViewport(true);
    });

    // Debounced resize handler
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => updateViewport(true), 300);
    });

    // HTMX events
    document.addEventListener('htmx:afterSettle', () => updateViewport(true));
    document.addEventListener('htmx:load', () => updateViewport(true));

    // Tab visibility change
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            updateViewport(false);
        }
    });
})();
"""

GRID_SCRIPT = r"""
(() => {
    const OBSERVER_OPTIONS = {
        rootMargin: '100px',
        threshold: [0, 0.1, 0.5]
    };

    let observerInstance = null;

    function loadImage(img) {
        return new Promise((resolve) => {
            const cell = img.closest('.grid-cell');
            const skeleton = cell?.querySelector('.grid-cell-skeleton');

            // Preload image to avoid visible loading jank
            const preloader = new Image();
            preloader.onload = () => {
                // Use requestAnimationFrame for smoother transitions
                requestAnimationFrame(() => {
                    img.src = preloader.src;
                    img.classList.add('loaded');
                    if (skeleton) {
                        skeleton.style.opacity = '0';
                        setTimeout(() => skeleton.remove(), 300);
                    }
                    resolve();
                });
            };

            preloader.onerror = () => {
                console.warn('Failed to load image:', img.dataset.src);
                if (skeleton) skeleton.remove();
                resolve();
            };

            // Start loading
            preloader.src = img.dataset.src;
        });
    }

    function getNeighbors(cell) {
        if (!cell) return [];

        const rect = cell.getBoundingClientRect();
        const cellSize = rect.width;
        const cells = Array.from(document.querySelectorAll('.grid-cell'));

        return cells.filter(neighbor => {
            if (neighbor === cell) return false;

            const nRect = neighbor.getBoundingClientRect();
            const distance = Math.hypot(
                rect.left - nRect.left,
                rect.top - nRect.top
            );

            return distance < cellSize * 1.5;
        });
    }

    function handleCellClick(cell) {
        const img = cell.querySelector('img');
        if (!img?.src) return; // Skip if image not loaded

        // Extract the path after /dataset/
        const match = img.src.match(/\/dataset\/(.+)$/);
        if (!match) {
            console.error('Could not extract image path from URL:', img.src);
            return;
        }

        const imagePath = match[1];

        // Add visual feedback
        cell.classList.add('processing');

        // Request caption
        fetch(`/api/generate-caption?image=${encodeURIComponent(imagePath)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.caption) {
                    console.log('Generated caption:', data.caption);
                    // Dispatch event to document level for better event bubbling
                    document.dispatchEvent(new CustomEvent('caption-generated', {
                        detail: { caption: data.caption },
                        bubbles: true
                    }));
                }
            })
            .catch(error => {
                console.error('Error getting caption:', error);
            })
            .finally(() => {
                cell.classList.remove('processing');
            });
    }

    function initializeGrid() {
        // Cleanup existing observer
        if (observerInstance) {
            observerInstance.disconnect();
            observerInstance = null;
        }

        const grid = document.querySelector('.grid-background');
        if (!grid) return;

        // Create new IntersectionObserver with optimized settings
        observerInstance = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;

                const cell = entry.target;
                const img = cell.querySelector('img');
                if (!img?.dataset.src || img.src) return;

                loadImage(img);
                observerInstance.unobserve(cell);
            });
        }, {
            // Increase root margin to start loading earlier
            rootMargin: '50% 50%',
            threshold: [0],
        });

        // Set up grid cells and start observing
        document.querySelectorAll('.grid-cell').forEach(cell => {
            // Start observing for lazy loading
            observerInstance.observe(cell);

            // Add hover handlers
            cell.addEventListener('mouseenter', () => {
                const neighbors = getNeighbors(cell);
                requestAnimationFrame(() => {
                    neighbors.forEach(n => n.classList.add('neighbor-hover'));
                });
            });

            cell.addEventListener('mouseleave', () => {
                requestAnimationFrame(() => {
                    document.querySelectorAll('.neighbor-hover')
                        .forEach(n => n.classList.remove('neighbor-hover'));
                });
            });

            // Add click handler for caption generation
            cell.addEventListener('click', () => handleCellClick(cell));
        });
    }

    // Initialize on load and after HTMX swaps
    document.addEventListener('htmx:afterSettle', initializeGrid);
    window.addEventListener('load', initializeGrid);

    // Cleanup on page unload
    window.addEventListener('unload', () => {
        if (observerInstance) {
            observerInstance.disconnect();
            observerInstance = null;
        }
    });
})();
"""


@dataclass
class GridManager:
    """Handles grid layout calculations and image management."""

    min_cell_size: int = 89
    gap: int = 5
    _image_cache: List[str] = field(default_factory=list)
    _layout_cache: Dict[Tuple[int, int], Tuple[int, int, int]] = field(
        default_factory=dict
    )

    def get_cached_images(self) -> List[str]:
        """Get or build cache of available images."""
        if not self._image_cache:
            image_dir = Path("dataset/flickr8k")
            # Use itertools.islice for memory-efficient slicing
            # Only process files in chunks
            self._image_cache = list(
                islice(
                    (str(p.relative_to("dataset")) for p in image_dir.glob("*.webp")),
                    0,
                    None,
                    1,
                )
            )
        return self._image_cache

    def calculate_layout(
        self, viewport_width: int, viewport_height: int
    ) -> Tuple[int, int, int]:
        """Calculate optimal grid layout to fully cover viewport with caching."""
        # Round dimensions to nearest 10px to improve cache hits
        cache_width = round(viewport_width / 10) * 10
        cache_height = round(viewport_height / 10) * 10
        cache_key = (cache_width, cache_height)

        # Check if we have this layout cached
        if cache_key in self._layout_cache:
            return self._layout_cache[cache_key]

        # If not in cache, calculate the layout
        padded_width = viewport_width + self.gap * 2
        padded_height = viewport_height + self.gap * 2
        aspect_ratio = viewport_width / viewport_height

        # Calculate initial number of columns that would fit
        cols = max(3, math.floor(padded_width / (self.min_cell_size + self.gap)))

        # Calculate cell size that exactly fits these columns
        cell_size = math.floor((padded_width - (cols * self.gap)) / cols)

        # Ensure we don't go below minimum cell size
        if cell_size < self.min_cell_size:
            cols = math.floor(padded_width / (self.min_cell_size + self.gap))
            cell_size = self.min_cell_size

        # Calculate rows needed to fully cover height
        rows = math.ceil(padded_height / (cell_size + self.gap))

        # Adjust for ultra-wide screens
        if aspect_ratio > 1.8:
            cols = math.ceil(cols * 1.2)  # Add 20% more columns

        # Cache the result
        result = (cell_size, cols, rows)
        self._layout_cache[cache_key] = result

        # Prevent cache from growing too large by removing oldest entries
        if len(self._layout_cache) > 100:  # Arbitrary limit
            del self._layout_cache[next(iter(self._layout_cache))]

        return result

    def select_images(self, total_cells: int) -> List[str]:
        """Select and randomize images for the grid with smart distribution."""
        available_images = self.get_cached_images()
        if not available_images:
            return []

        # Create a pool of randomized images that can be reshuffled
        image_pool = available_images.copy()
        random.shuffle(image_pool)

        selected_images = []
        while len(selected_images) < total_cells:
            if not image_pool:
                image_pool = available_images.copy()
                random.shuffle(image_pool)
            selected_images.append(image_pool.pop())

        return selected_images

    def create_grid_cells(
        self, viewport_width: int, viewport_height: int
    ) -> Tuple[List[Any], Dict[str, Union[str, int]]]:
        """Create grid cells and return with layout variables."""
        cell_size, column_count, row_count = self.calculate_layout(
            viewport_width, viewport_height
        )

        # Calculate total cells needed
        total_cells = column_count * row_count

        # Select and prepare images
        selected_images = self.select_images(total_cells)
        if not selected_images:
            return [], {}

        # Create grid cells with optimized loading
        cells = []
        for idx, img_path in enumerate(selected_images):
            cells.append(
                Div(
                    Div(cls="grid-cell-skeleton"),
                    Img(
                        data_src=f"/dataset/{img_path}",
                        alt="",
                        loading="lazy",
                        # Add explicit dimensions to prevent layout shifts
                        width=str(cell_size),
                        height=str(cell_size),
                        # Lower fetch priority for background images
                        fetchpriority="low",
                        cls="grid-cell-image opacity-0",
                    ),
                    cls="grid-cell",
                    style=f"""
                        --cell-size: {cell_size}px;
                        --cell-index: {idx};
                        --grid-cell-delay: {idx % (column_count * 2)};
                    """,
                )
            )

        # Create layout variables
        layout_vars = {
            "--cell-size": f"{cell_size}px",
            "--column-count": str(column_count),
            "--row-count": str(row_count),
            "--viewport-width": f"{viewport_width}px",
            "--viewport-height": f"{viewport_height}px",
            "--grid-gap": f"{self.gap}px",
        }

        return cells, layout_vars


@dataclass
class GridBackground:
    """Dynamic grid background with image cells and visual effects.

    Creates a responsive grid of images that serves as a background layer,
    with hover effects and performant loading.

    Args:
        content: Content to overlay on top of the grid
        min_cols: Minimum number of columns in the grid (default: 8)
        gap: Gap between grid cells in pixels (default: 5)
        cls: Additional CSS classes
        attrs: Additional HTML attributes
    """

    content: Union[Any, Tuple[Any, ...]]
    min_cols: int = 8
    gap: int = 5
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)
    content_attrs: Dict = field(default_factory=dict)

    def _get_content_elements(self) -> list:
        """Convert content to list if it's a single item."""
        return (
            [self.content]
            if not isinstance(self.content, (list, tuple))
            else list(self.content)
        )

    def __ft__(self):
        """Convert to FastHTML FT component."""
        grid = Div(
            # Hidden viewport tracking inputs
            Div(
                Input(
                    type="hidden",
                    name="viewport-width",
                    id="viewport-width",
                    value="0",  # Start with 0 to ensure initial update
                ),
                Input(
                    type="hidden",
                    name="viewport-height",
                    id="viewport-height",
                    value="0",  # Start with 0 to ensure initial update
                ),
                cls="hidden",
            ),
            cls=f"grid-background {self.cls or ''}",
            style=f"--grid-gap: {self.gap}px",
            hx_get="/api/grid-images",
            hx_trigger="size-update",
            hx_include="#viewport-width, #viewport-height",
            hx_swap="innerHTML",
            **self.attrs,
        )

        content = Div(
            *self._get_content_elements(),
            cls=f"grid-content {self.content_attrs.pop('cls', '')}",
            **self.content_attrs,
        )

        return Div(
            Style(GRID_STYLES),
            grid,
            content,
            Script(VIEWPORT_SCRIPT),
            Script(GRID_SCRIPT),
            cls="relative h-dvh",
        )


def grid_background(*content: Any, **kwargs) -> GridBackground:
    """Create a GridBackground instance with smart parameter handling.

    Args:
        *content: Variable number of child elements
        **kwargs: GridBackground configuration parameters

    Returns:
        GridBackground: A configured GridBackground instance
    """
    # Separate GridBackground params from HTML attributes
    params = {k: v for k, v in kwargs.items() if k in GRID_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in GRID_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return GridBackground(content, **params)
