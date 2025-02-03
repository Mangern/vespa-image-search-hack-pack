from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, Tuple, Union

from fasthtml.common import Body as BaseBody

# Constants
BODY_PARAMS: Set[str] = {
    "is_home",
    "cls",
}

CLASS_GROUPS: Dict[str, str] = {
    "dimensions": "min-h-0 h-dvh",
}


@dataclass
class Body:
    """Core layout component that structures the page with header and content areas.

    Creates a grid layout with a fixed-height header row and a flexible content row.
    Uses proper HTML body semantics via FastHTML's BaseBody component.

    Args:
        content: Child elements (typically Header followed by Main/Aside).
                Can be single item or tuple/list.
        is_home: Whether this is the home page layout
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes

    Notes:
        The body component automatically adds a data-is-home attribute
        that can be targeted in CSS:

            body[data-is-home="true"] {
                // Home page specific styles
            }
    """

    content: Union[Any, Tuple[Any, ...]]
    is_home: bool = False
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the body element."""
        return [
            CLASS_GROUPS["dimensions"],
            # Additional custom classes
            self.cls or "",
        ]

    def _get_content_elements(self) -> list:
        """Convert content to a list if it's a single item."""
        return (
            [self.content]
            if not isinstance(self.content, (list, tuple))
            else list(self.content)
        )

    def _prepare_attributes(self) -> Dict:
        """Prepare HTML attributes including data attributes."""
        attrs = self.attrs.copy()
        attrs["data-is-home"] = str(self.is_home).lower()
        return attrs

    def __ft__(self):
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content = self._get_content_elements()
        attrs = self._prepare_attributes()

        return BaseBody(*content, cls=" ".join(filter(None, classes)), **attrs)


def body(*content: Any, **kwargs) -> Body:
    """Create a Body instance with smart parameter handling.

    This function provides a convenient way to create Body instances with
    multiple child elements and configuration options.

    Args:
        *content: Variable number of child elements
        **kwargs: Body configuration parameters

    Returns:
        Body: A configured Body instance

    """
    theme_bg = "bg-app-background"
    theme_text = "text-high-contrast-text"
    theme_layout = "grid grid-rows-[minmax(0,55px)_minmax(0,1fr)]"

    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        has_bg = any(cls.startswith("bg-") for cls in custom_classes.split())
        has_text = any(cls.startswith("text-") for cls in custom_classes.split())
        has_layout = any(
            cls.startswith(("grid-", "flex-", "grid")) for cls in custom_classes.split()
        )

        default_classes = []
        if not has_bg:
            default_classes.append(theme_bg)
        if not has_text:
            default_classes.append(theme_text)
        if not has_layout:
            default_classes.append(theme_layout)

        kwargs["cls"] = f"{' '.join(default_classes)} {custom_classes}".strip()
    else:
        kwargs["cls"] = f"{theme_bg} {theme_text} {theme_layout}"

    # Separate kwargs into Body params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in BODY_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in BODY_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Body(content, **params)
