from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, Tuple, Union

from fasthtml.common import Main as BaseMain

# Constants
MAIN_PARAMS: Set[str] = {
    "cls",
}

CLASS_GROUPS: Dict[str, str] = {
    "dimensions": "h-full",
}


@dataclass
class Main:
    """Primary content wrapper component.

    Represents the main content area of the document.
    Automatically handles padding, overflow, and grid positioning.
    Uses proper HTML main semantics via FastHTML's BaseMain component.

    Args:
        content: Child elements for the main content area.
                Can be single item or tuple/list.
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes

    Examples:
        >>> # Basic usage with single content
        >>> main(
        ...     Article(...)
        ... )

        >>> # Multiple content sections
        >>> main(
        ...     Article(...),
        ...     Section(...),
        ...     Section(...),
        ...     cls="custom-spacing"
        ... )
    """

    content: Union[Any, Tuple[Any, ...]]
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the main element."""
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

    def __ft__(self):
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content = self._get_content_elements()

        return BaseMain(*content, cls=" ".join(filter(None, classes)), **self.attrs)


def main(*content: Any, **kwargs) -> Main:
    """Create a Main instance with smart parameter handling.

    This function provides a convenient way to create Main instances with
    multiple child elements.

    Args:
        *content: Variable number of child elements
        **kwargs: Main configuration parameters

    Returns:
        Main: A configured Main instance

    Examples:
        >>> # Basic usage
        >>> main(Article())

        >>> # Multiple sections with custom class
        >>> main(
        ...     Article(),
        ...     Section(),
        ...     cls="custom-spacing"
        ... )
    """
    theme_classes = "overflow-auto"

    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        has_overflow = any(cls.startswith("overflow-") for cls in custom_classes.split())

        if not has_overflow:
            kwargs["cls"] = f"{theme_classes} {custom_classes}"
    else:
        kwargs["cls"] = theme_classes

    # Separate kwargs into Main params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in MAIN_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in MAIN_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Main(content, **params)
