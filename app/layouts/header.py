from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, Tuple, Union

from fasthtml.common import Header as BaseHeader

# Constants
HEADER_PARAMS: Set[str] = {
    "is_home",
    "cls",
}

CLASS_GROUPS: Dict[str, str] = {
    "layout": "col-span-full min-h-[55px] h-[55px] w-full",
    "flex": "flex items-center justify-between",
    "spacing": "px-md",
    "theme": "border-b",
}


@dataclass
class Header:
    """Top-level header component for the application.

    Represents the main header that spans the top of the page.
    Contains navigation elements, branding, and global actions.

    Args:
        content: Child elements for the header. Can be single item or tuple/list.
        is_home: Whether this header is on the home page (affects behavior)
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes

    Examples:
        >>> # Basic usage with logo and nav
        >>> header(
        ...     Logo(),
        ...     Nav(
        ...         ThemeToggle(),
        ...         UserMenu()
        ...     )
        ... )

        >>> # With separate sections
        >>> header(
        ...     Div(Logo(), cls="flex items-center"),
        ...     Div(
        ...         ThemeToggle(),
        ...         UserMenu(),
        ...         cls="flex items-center gap-sm"
        ...     ),
        ...     is_home=True
        ... )
    """

    content: Union[Any, Tuple[Any, ...]]
    is_home: bool = False
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the header."""
        return [
            # Grouped classes for better organization
            CLASS_GROUPS["layout"],
            CLASS_GROUPS["flex"],
            CLASS_GROUPS["spacing"],
            CLASS_GROUPS["theme"],
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

        return BaseHeader(*content, cls=" ".join(filter(None, classes)), **attrs)


def header(*content: Any, **kwargs) -> Header:
    """Create a Header instance with smart parameter handling.

    This function provides a convenient way to create Header instances with
    multiple child elements.

    Args:
        *content: Variable number of child elements
        **kwargs: Header configuration parameters

    Returns:
        Header: A configured Header instance

    Examples:
        >>> # Basic usage
        >>> header(Logo(), MainNav())

        >>> # With is_home flag
        >>> header(
        ...     Logo(),
        ...     MainNav(),
        ...     is_home=True
        ... )
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

    params = {k: v for k, v in kwargs.items() if k in HEADER_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in HEADER_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Header(content, **params)
