from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Union

from fasthtml.common import Div

# Constants
TOOLBAR_PARAMS: Set[str] = {
    "is_sticky",
    "compact",
    "cls",
}

# Height values following Fibonacci sequence (34, 55)
HEIGHTS = {
    "default": "min-h-[55px] h-[55px]",
    "compact": "min-h-[34px] h-[34px]",
}

CLASS_GROUPS: Dict[str, str] = {
    "layout": "col-span-full w-full",  # Height is added dynamically
    "flex": "flex items-center justify-between",
    "spacing": "px-md",
    "theme": "border-b",
    "sticky": "sticky top-[55px] z-40",  # z-index just below header
}


@dataclass
class Toolbar:
    """Secondary navigation bar component for the application.

    Represents a toolbar that can be placed below the header for additional
    navigation or action items. Follows Fibonacci scale for height values (34px, 55px).

    Args:
        content: Child elements for the toolbar. Can be single item or tuple/list.
        is_sticky: Whether the toolbar should stick to top when scrolling
        compact: Use compact height (34px) instead of default (55px)
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes
    """

    content: Optional[Union[Any, Tuple[Any, ...]]] = None
    is_sticky: bool = False
    compact: bool = False
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the toolbar."""
        classes = [
            CLASS_GROUPS["layout"],
            HEIGHTS["compact"] if self.compact else HEIGHTS["default"],
            CLASS_GROUPS["flex"],
            CLASS_GROUPS["spacing"],
            CLASS_GROUPS["theme"],
        ]

        if self.is_sticky:
            classes.append(CLASS_GROUPS["sticky"])

        if self.cls:
            classes.append(self.cls)

        return classes

    def _get_content_elements(self) -> list[Any]:
        """Get content elements from either content property or attrs."""
        # If we have content passed directly, use that
        if self.content is not None:
            return (
                [self.content]
                if not isinstance(self.content, (list, tuple))
                else list(self.content)
            )

        # If we have content in attrs, extract and remove it
        content: Optional[Iterable[Any]] = self.attrs.pop("content", None)
        if content is not None:
            return [content] if not isinstance(content, (list, tuple)) else list(content)

        return []

    def _prepare_attributes(self) -> Dict:
        """Prepare HTML attributes including data attributes."""
        attrs = self.attrs.copy()
        attrs["data-is-sticky"] = str(self.is_sticky).lower()
        attrs["data-compact"] = str(self.compact).lower()
        return attrs

    def __ft__(self):
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content = self._get_content_elements()
        attrs = self._prepare_attributes()

        return Div(*content, cls=" ".join(filter(None, classes)), **attrs)


def toolbar(*content: Any, **kwargs) -> Toolbar:
    """Create a Toolbar instance with smart parameter handling.

    This function provides a convenient way to create Toolbar instances with
    multiple child elements. The toolbar can be configured to use either default (55px)
    or compact (34px) height following the Fibonacci sequence.

    Content can be passed either as children or via the content property in kwargs.

    Args:
        *content: Variable number of child elements
        **kwargs: Toolbar configuration parameters

    Returns:
        Toolbar: A configured Toolbar instance
    """
    theme_bg = "bg-subtle-background"
    theme_border = "border-subtle-border-and-separator"

    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        has_bg = any(cls.startswith("bg-") for cls in custom_classes.split())
        has_border = any(cls.startswith("border-") for cls in custom_classes.split())

        default_classes = []
        if not has_bg:
            default_classes.append(theme_bg)
        if not has_border:
            default_classes.append(theme_border)

        kwargs["cls"] = f"{' '.join(default_classes)} {custom_classes}".strip()
    else:
        kwargs["cls"] = f"{theme_bg} {theme_border}"

    params = {k: v for k, v in kwargs.items() if k in TOOLBAR_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in TOOLBAR_PARAMS}

    if attrs:
        params["attrs"] = attrs

    # If content is passed as children, prioritize it over content in attrs
    if content:
        return Toolbar(content, **params)
    return Toolbar(**params)
