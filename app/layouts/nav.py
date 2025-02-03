from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, Tuple, Union

from fasthtml.common import Nav as BaseNav

# Constants
NAV_PARAMS: Set[str] = {
    "cls",
}

CLASS_GROUPS: Dict[str, str] = {
    "layout": "flex items-center",
}


@dataclass
class Nav:
    """Navigation component that groups navigation items.

    A flexible nav component that provides proper semantic markup and styling
    for navigation sections, typically used in the header or sidebars.

    Args:
        content: Navigation items (typically links or buttons).
                Can be single item or tuple/list.
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes

    Examples:
        >>> # Basic usage
        >>> nav(A("Home"), A("About"))

        >>> # With custom styling
        >>> nav(
        ...     A("Home"),
        ...     A("About"),
        ...     cls="custom-spacing"
        ... )
    """

    content: Union[Any, Tuple[Any, ...]]
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the nav element."""
        return [
            # Grouped classes for better organization
            CLASS_GROUPS["layout"],
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

    def __ft__(self):
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content = self._get_content_elements()

        return BaseNav(*content, cls=" ".join(filter(None, classes)), **self.attrs)


def nav(*content: Any, **kwargs) -> Nav:
    """Create a Nav instance with smart parameter handling.

    This function provides a convenient way to create Nav instances with
    multiple child elements.

    Args:
        *content: Variable number of child elements
        **kwargs: Nav configuration parameters

    Returns:
        Nav: A configured Nav instance

    Examples:
        >>> # Basic usage
        >>> nav(A("Home"), A("About"))

        >>> # With custom classes
        >>> nav(
        ...     A("Home"),
        ...     A("About"),
        ...     cls="custom-spacing"
        ... )
    """
    spacing_class = "gap-sm md:gap-lg"

    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        has_gap = any(cls.startswith("gap-") for cls in custom_classes.split())

        if not has_gap:
            kwargs["cls"] = f"{spacing_class} {custom_classes}"
    else:
        kwargs["cls"] = spacing_class

    # Separate kwargs into Nav params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in NAV_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in NAV_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Nav(content, **params)
