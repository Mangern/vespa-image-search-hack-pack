from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

from fasthtml.common import Div, Img, P, Script, Style

PHI = 1.618033988749895
CDN_BASE = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5"
STATIC_RESOURCES = (Script(src=f"{CDN_BASE}/gsap.min.js"),)

GRID_PARAMS: Set[str] = {
    "cls",
    "duration",
    "ease",
    "scale",
    "spread",
    "max_rotation",
    "max_distance",
    "gap",
}

GRID_STYLES = """
.search-results-container {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.search-results-grid {
    width: 100%;
    height: 100%;
    display: grid;
    gap: var(--grid-gap, 13px);
    padding: var(--grid-gap, 13px);
    grid-template-columns: repeat(5, minmax(0, 1fr));
    grid-auto-rows: calc((100% - (4 * var(--grid-gap, 13px))) / 5);
    grid-auto-flow: row;
}

.search-results-item {
    position: relative;
    margin: 0;
    will-change: transform;
    pointer-events: auto;
    overflow: hidden;
    cursor: pointer;
    z-index: 1;
    background: var(--ui-element-background);
    display: flex;
    align-items: center;
    justify-content: center;
}

.search-results-item-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    opacity: 0;
    transform: scale(1.1);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    will-change: transform, opacity;
    loading: lazy;
    decoding: async;
    padding: calc(var(--grid-gap, 13px) * 0.5);
}

.search-results-item-img.loaded {
    opacity: 1;
    transform: scale(1);
    filter: brightness(1.1) saturate(1.2) contrast(1.05);
}

.search-results-item-skeleton {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        110deg,
        var(--subtle-background) 0%,
        var(--ui-element-background) 38.2%,
        var(--subtle-background) 61.8%
    );
    background-size: 200% 100%;
    animation: search-results-skeleton 1.618s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes search-results-skeleton {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.search-results-caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: calc(var(--grid-gap) * 0.618);
    background: linear-gradient(
        to bottom,
        transparent,
        rgba(0, 0, 0, 0.618)
    );
    color: white;
    opacity: 0;
    transform: translateY(61.8%);
    transition: all 0.618s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-results-item:hover .search-results-caption {
    opacity: 1;
    transform: translateY(0);
}

.search-results-empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: calc(var(--grid-gap) * 2.618);
    background: var(--subtle-background);
    border-radius: calc(var(--grid-gap) * 0.618);
    aspect-ratio: var(--golden-ratio);
    display: grid;
    place-items: center;
}

.search-results-item.processing::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--app-background);
    opacity: 0.618;
    z-index: 3;
}

.search-results-item.processing::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: calc(var(--grid-gap) * 1.618);
    height: calc(var(--grid-gap) * 1.618);
    margin: calc(var(--grid-gap) * -0.809) 0 0 calc(var(--grid-gap) * -0.809);
    border: 2px solid transparent;
    border-top-color: var(--solid-background);
    border-radius: 50%;
    animation: spinner 1.618s linear infinite;
    z-index: 4;
}

@keyframes spinner {
    to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
    .search-results-item-img {
        transition: opacity 0.1s linear;
    }
    .search-results-item:hover .search-results-item-img {
        transform: none;
    }
}
"""

GRID_SCRIPT = """
(() => {
    const OBSERVER_OPTIONS = {
        rootMargin: '100px',
        threshold: [0, 0.1, 0.5]
    };

    let observerInstance = null;
    let expandedItem = -1;
    let previousExpanded = -1;
    let tl;

    function loadImage(element) {
        const skeleton = element.querySelector(".search-results-item-skeleton");
        const img = element.querySelector(".search-results-item-img");
        const src = img?.dataset?.src;

        if (!img || !src) {
            if (skeleton) skeleton.remove();
            return Promise.resolve();
        }

        return new Promise((resolve) => {
            const tempImage = new Image();

            const cleanup = () => {
                tempImage.onload = null;
                tempImage.onerror = null;
                if (skeleton) skeleton.remove();
                resolve();
            };

            tempImage.onload = () => {
                requestAnimationFrame(() => {
                    img.src = src;
                    img.classList.add("loaded");
                    cleanup();
                });
            };

            tempImage.onerror = () => {
                console.warn("Failed to load image:", src);
                cleanup();
            };

            tempImage.src = src;
        });
    }

    function getTranslationDistance(element1, element2, spread = 80, maxDistance = 500) {
        const el1Rect = element1.getBoundingClientRect();
        const el2Rect = element2.getBoundingClientRect();

        const elCenter = {
            x: el1Rect.left + el1Rect.width/2,
            y: el1Rect.top + el1Rect.height/2
        };
        const elCenter2 = {
            x: el2Rect.left + el2Rect.width/2,
            y: el2Rect.top + el2Rect.height/2
        };

        const distance = Math.hypot(elCenter.x - elCenter2.x, elCenter.y - elCenter2.y);
        spread = Math.max(map(distance, 0, maxDistance, spread, 0), 0);

        const angle = Math.atan2(Math.abs(elCenter2.y - elCenter.y), Math.abs(elCenter2.x - elCenter.x));

        let x = Math.abs(Math.cos(angle) * spread);
        let y = Math.abs(Math.sin(angle) * spread);

        return {
            x: elCenter.x < elCenter2.x ? x*-1 : x,
            y: elCenter.y < elCenter2.y ? y*-1 : y
        };
    }

    function map(x, a, b, c, d) {
        return (x - a) * (d - c) / (b - a) + c;
    }

    function getDistance(element1, element2) {
        const el1Rect = element1.getBoundingClientRect();
        const el2Rect = element2.getBoundingClientRect();

        const elCenter = {
            x: el1Rect.left + el1Rect.width/2,
            y: el1Rect.top + el1Rect.height/2
        };
        const elCenter2 = {
            x: el2Rect.left + el2Rect.width/2,
            y: el2Rect.top + el2Rect.height/2
        };

        return Math.hypot(elCenter.x - elCenter2.x, elCenter.y - elCenter2.y);
    }

    function expand(grid, item) {
        if (!grid || !item || !window.gsap) return;

        const itemIdx = Array.from(grid.querySelectorAll(".search-results-item")).indexOf(item);

        if (tl) {
            tl.kill();
            tl = null;
        }

        previousExpanded = expandedItem !== -1 && expandedItem !== itemIdx ? expandedItem : -1;
        expandedItem = expandedItem === itemIdx ? -1 : itemIdx;

        const options = {
            duration: parseFloat(grid.dataset.duration || "0.8"),
            ease: grid.dataset.ease || "power3.out",
            scale: parseFloat(grid.dataset.scale || "2.5"),
            spread: parseFloat(grid.dataset.spread || "150"),
            maxRotation: parseFloat(grid.dataset.maxRotation || "6"),
            maxDistance: parseFloat(grid.dataset.maxDistance || "1000")
        };

        tl = gsap.timeline({
            defaults: { duration: options.duration, ease: options.ease }
        });

        // Main item animation
        tl.set(item, {
            zIndex: expandedItem === -1 ? 1 : 999
        }, 0).to(item, {
            scale: expandedItem === -1 ? 1 : options.scale,
            x: 0,
            y: 0,
            rotation: 0
        }, 0);

        // Handle previous expanded item
        if (previousExpanded !== -1) {
            const prevItem = grid.querySelectorAll(".search-results-item")[previousExpanded];
            if (prevItem) {
                tl.set(prevItem, { zIndex: 1 }, 0)
                  .to(prevItem, {
                      scale: 1,
                      x: 0,
                      y: 0,
                      rotation: 0
                  }, 0);
            }
        }

        // Handle other items
        const otherItems = Array.from(grid.querySelectorAll(".search-results-item"))
            .filter(otherItem => otherItem !== item);

        otherItems.forEach(otherItem => {
            const {x, y} = expandedItem === -1
                ? {x: 0, y: 0}
                : getTranslationDistance(otherItem, item, options.spread, options.maxDistance);

            const zIndex = Math.round(map(
                getDistance(otherItem, item),
                0,
                100000,
                998,
                1
            ));

            const rotation = expandedItem === -1
                ? 0
                : gsap.utils.random(options.maxRotation * -1, options.maxRotation);

            tl.set(otherItem, {
                zIndex: expandedItem === -1 ? 1 : zIndex
            }, 0).to(otherItem, {
                x, y, rotation
            }, 0);
        });
    }

    function initializeGrid() {
        if (observerInstance) {
            observerInstance.disconnect();
            observerInstance = null;
        }

        const grid = document.querySelector('.search-results-grid');
        if (!grid) return;

        observerInstance = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                loadImage(entry.target);
                observerInstance.unobserve(entry.target);
            });
        }, OBSERVER_OPTIONS);

        document.querySelectorAll(".search-results-item").forEach(item => {
            const oldHandler = item._expandHandler;
            if (oldHandler) {
                item.removeEventListener("click", oldHandler);
            }

            const handler = () => expand(grid, item);
            item._expandHandler = handler;
            item.addEventListener("click", handler);

            observerInstance.observe(item);
        });
    }

    function cleanup() {
        if (observerInstance) {
            observerInstance.disconnect();
            observerInstance = null;
        }
        if (tl) {
            tl.kill();
            tl = null;
        }
        gsap.killTweensOf(".search-results-item");

        document.querySelectorAll(".search-results-item").forEach(item => {
            if (item._expandHandler) {
                item.removeEventListener("click", item._expandHandler);
                delete item._expandHandler;
            }
        });
    }

    document.addEventListener('htmx:afterSettle', initializeGrid);
    window.addEventListener('load', initializeGrid);
    window.addEventListener('beforeunload', cleanup);
    document.addEventListener('htmx:beforeCleanupElement', cleanup);
})();
"""


@dataclass
class EmptySearchResults:
    query: Optional[str] = None
    message: Optional[str] = None
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def get_message(self) -> str:
        """Get appropriate message based on context."""
        if self.message:
            return self.message

        return (
            "No results found. Try adjusting your search terms."
            if self.query
            else "Enter a query to explore."
        )

    def __ft__(self):
        return Div(
            P(self.get_message()),
            cls=f"grid place-content-center h-full {self.cls or ''}",
            **self.attrs,
        )


@dataclass
class SearchResultsGrid:
    """Grid component for displaying search results with animations."""

    images: List[Union[str, Dict[str, str]]]
    duration: float = 0.8
    ease: str = "power3.out"
    scale: float = 2.2
    spread: float = 120
    max_rotation: float = 6
    max_distance: float = 800
    gap: int = 13
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    @staticmethod
    def create_grid_item(image_data: Union[str, Dict[str, str]]) -> Any:
        """Create a grid item with lazy loading."""
        if isinstance(image_data, str):
            image_path = image_data
            caption = None
        else:
            image_path = image_data.get("path", "")
            caption = image_data.get("caption")

        return Div(
            Div(cls="search-results-item-skeleton"),
            Img(
                cls="search-results-item-img",
                data_src=f"/dataset/{image_path}",
                loading="lazy",
                alt=caption or "Search result image",
            ),
            Div(P(caption), cls="search-results-caption") if caption else None,
            cls="search-results-item",
        )

    def __ft__(self):
        """Convert to FastHTML FT component."""
        grid = Div(
            *[self.create_grid_item(img) for img in self.images],
            cls=f"search-results-grid {self.cls or ''}",
            style=f"--grid-gap: {self.gap}px; --golden-ratio: {PHI};",
            data_duration=str(self.duration),
            data_ease=self.ease,
            data_scale=str(self.scale),
            data_spread=str(self.spread),
            data_max_rotation=str(self.max_rotation),
            data_max_distance=str(self.max_distance),
            **self.attrs,
        )

        return Div(
            Style(GRID_STYLES),
            grid,
            *STATIC_RESOURCES,
            Script(GRID_SCRIPT),
            cls="search-results-container",
        )


def search_results_grid(*images: Any, **kwargs) -> SearchResultsGrid:
    """Create a SearchResultsGrid instance with smart parameter handling.

    Args:
        *images: Variable number of image paths or image data dictionaries
        **kwargs: Grid configuration parameters and HTML attributes

    Returns:
        SearchResultsGrid: A configured grid instance
    """
    if len(images) == 1 and isinstance(images[0], (list, tuple)):
        images = images[0]

    grid_params = {k: v for k, v in kwargs.items() if k in GRID_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in GRID_PARAMS}

    if attrs:
        grid_params["attrs"] = attrs

    return SearchResultsGrid(list(images), **grid_params)
