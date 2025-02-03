from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Set, Tuple, Union

from fasthtml.common import Script

# Type definitions
GridColumns = Literal[
    "grid-cols-1",
    "md:grid-cols-[auto_1fr]",
    "md:grid-cols-[1fr_auto]",
    "md:grid-cols-[auto_1fr_auto]",
]

# Constants
LAYOUT_PARAMS: Set[str] = {
    "cls",
}

GRID_CLASSES: Dict[str, GridColumns] = {
    "single": "grid-cols-1",
    "left_sidebar": "md:grid-cols-[auto_1fr]",
    "right_sidebar": "md:grid-cols-[1fr_auto]",
    "both_sidebars": "md:grid-cols-[auto_1fr_auto]",
}

LAYOUT_SCRIPT = """
    document.addEventListener("DOMContentLoaded", function() {{
        function updateLayout() {{
            const main = document.querySelector("main");
            const asides = document.querySelectorAll("aside");
            const body = document.body;

            // Grid class mappings
            const GRID_CLASSES = {{
                single: "{single}",
                leftSidebar: "{left_sidebar}",
                rightSidebar: "{right_sidebar}",
                bothSidebars: "{both_sidebars}"
            }};

            // Remove existing grid classes
            body.classList.remove(
                GRID_CLASSES.single,
                GRID_CLASSES.leftSidebar,
                GRID_CLASSES.rightSidebar,
                GRID_CLASSES.bothSidebars
            );

            if (main && asides.length > 0) {{
                if (asides.length === 1) {{
                    const aside = asides[0];
                    const position = aside.dataset.position;

                    if (position === "left") {{
                        body.classList.add(GRID_CLASSES.leftSidebar);
                    }} else {{
                        body.classList.add(GRID_CLASSES.rightSidebar);
                    }}
                }} else if (asides.length === 2) {{
                    body.classList.add(GRID_CLASSES.bothSidebars);
                }}
            }} else if (main) {{
                body.classList.add(GRID_CLASSES.single);
            }}
        }}

        updateLayout();
    }});
"""


@dataclass
class Layout:
    """Top-level layout wrapper that manages the overall page structure.

    A flexible layout component that handles responsive behavior and manages
    the grid structure for main content and optional sidebars. It automatically
    adjusts the grid layout based on the presence and position of sidebars.

    Args:
        content: Child elements (typically Title and Body components).
                Can be single item or tuple/list.
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes
    """

    content: Union[Any, Tuple[Any, ...]]
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_content_elements(self) -> list:
        """Convert content to a list if it's a single item."""
        return (
            [self.content]
            if not isinstance(self.content, (list, tuple))
            else list(self.content)
        )

    @staticmethod
    def _prepare_layout_script() -> Script:
        """Create the script component for managing responsive behavior."""
        return Script(
            LAYOUT_SCRIPT.format(
                single=GRID_CLASSES["single"],
                left_sidebar=GRID_CLASSES["left_sidebar"],
                right_sidebar=GRID_CLASSES["right_sidebar"],
                both_sidebars=GRID_CLASSES["both_sidebars"],
            )
        )

    def __ft__(self):
        """Convert to FastHTML FT component."""
        content = self._get_content_elements()
        return *content, self._prepare_layout_script()


def layout(*content: Any, **kwargs) -> Layout:
    """Create a Layout instance with smart parameter handling.

    This function provides a convenient way to create Layout instances with
    multiple child elements.

    Args:
        *content: Variable number of child elements
        **kwargs: Layout configuration parameters

    Returns:
        Layout: A configured Layout instance
    """
    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        kwargs["cls"] = f"{custom_classes}"

    # Separate kwargs into Layout params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in LAYOUT_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in LAYOUT_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Layout(content, **params)
