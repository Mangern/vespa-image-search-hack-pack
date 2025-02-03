from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Tuple, Union

from fasthtml.common import Div

AlignItems = Literal["start", "center", "end", "stretch", "baseline"]
JustifyContent = Literal["start", "center", "end", "between", "around", "evenly"]
FlexWrap = Literal["wrap", "nowrap", "wrap-reverse"]

ALIGN_CLASSES: Dict[str, str] = {
    "start": "items-start",
    "center": "items-center",
    "end": "items-end",
    "stretch": "items-stretch",
    "baseline": "items-baseline",
}

JUSTIFY_CLASSES: Dict[str, str] = {
    "start": "justify-start",
    "center": "justify-center",
    "end": "justify-end",
    "between": "justify-between",
    "around": "justify-around",
    "evenly": "justify-evenly",
}

WRAP_CLASSES: Dict[str, str] = {
    "wrap": "flex-wrap",
    "nowrap": "flex-nowrap",
    "wrap-reverse": "flex-wrap-reverse",
}

GROUP_PARAMS: set[str] = {
    "align",
    "justify",
    "wrap",
    "grow",
    "cls",
}


@dataclass
class Group:
    """A flex container for horizontal layouts.

    Creates a flexbox container that arranges children horizontally with
    configurable alignment, justification, and wrapping behavior.

    Args:
        content: Group children elements (single element or tuple of elements)
        align: Controls align-items CSS property
        justify: Controls justify-content CSS property
        wrap: Controls flex-wrap CSS property
        grow: Whether children should grow to fill space
        cls: Additional CSS classes
        attrs: Additional HTML attributes

    Examples:
        >>> group(Div("hello"), Div("world"))  # Basic usage
        >>> group(
        ...     Div("One"),
        ...     Div("Two"),
        ...     align="center",
        ...     justify="between",
        ...     cls="gap-lg"
        ... )
    """

    content: Union[Any, Tuple[Any, ...]]
    align: AlignItems = "center"
    justify: JustifyContent = "start"
    wrap: FlexWrap = "wrap"
    grow: bool = False
    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the group container."""
        return [
            # Base styles
            "flex",
            # Alignment
            ALIGN_CLASSES[self.align],
            # Justification
            JUSTIFY_CLASSES[self.justify],
            # Wrap
            WRAP_CLASSES[self.wrap],
            # Additional classes
            self.cls or "",
        ]

    def _get_content_elements(self) -> list:
        """Process and return the content elements."""
        # Convert single element to list if needed
        content = (
            [self.content]
            if not isinstance(self.content, (list, tuple))
            else self.content
        )

        # Apply grow styles if enabled
        if self.grow:
            return [
                Div(
                    child,
                    cls="flex-grow basis-0 min-w-0",  # basis-0 ensures equal width distribution
                )
                for child in content
            ]

        return content

    def __ft__(self) -> Div:
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content_elements = self._get_content_elements()

        return Div(*content_elements, cls=" ".join(filter(None, classes)), **self.attrs)


def group(*content: Any, **kwargs) -> Group:
    """Create a Group instance for horizontal layouts.

    This function provides a convenient way to create Group instances with
    multiple child elements and default styling.

    Args:
        *content: Variable number of child elements
        **kwargs: Group configuration parameters

    Returns:
        Group: A configured Group instance

    Examples:
        >>> group(Div("hello"), Div("world"))
        >>> group(
        ...     Div("One"),
        ...     Div("Two"),
        ...     justify="end",
        ...     cls="gap-sm bg-subtle"
        ... )
    """
    # Default spacing between elements
    default_classes = "gap-md"

    # If cls is provided, append to defaults
    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        # Check if custom classes contain gap utilities
        has_gap = any(cls.startswith("gap-") for cls in custom_classes.split())
        # Only add default gap if no custom gap is specified
        kwargs["cls"] = (
            custom_classes if has_gap else f"{default_classes} {custom_classes}"
        )
    else:
        kwargs["cls"] = default_classes

    # Separate kwargs into Group params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in GROUP_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in GROUP_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Group(content, **params)
