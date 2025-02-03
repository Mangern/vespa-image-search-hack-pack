from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Set, Tuple, Union

from fasthtml.common import Div

ContainerSize = Literal["sm", "md", "lg", "xl", "2xl"]

# Constants - Using standard Tailwind breakpoint widths
SIZE_CLASSES: Dict[str, str] = {
    "sm": "max-w-[640px]",  # sm breakpoint
    "md": "max-w-[768px]",  # md breakpoint
    "lg": "max-w-[1024px]",  # lg breakpoint
    "xl": "max-w-[1280px]",  # xl breakpoint
    "2xl": "max-w-[1536px]",  # 2xl breakpoint
}

CONTAINER_PARAMS: Set[str] = {
    "fluid",
    "size",
    "cls",
}


@dataclass
class Container:
    """A responsive container component with configurable max-width.

    Creates a grid container that can either be fluid (full-width) or have a
    specific max-width based on Tailwind's standard breakpoints.

    Args:
        content: Child elements to be contained
        fluid: Whether the container should be full-width
        size: Maximum width based on standard Tailwind breakpoints:
              sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
        cls: Additional CSS classes
        attrs: Additional HTML attributes

    Examples:
        >>> container(Div(...))  # Default contained width (md - 768px)
        >>> container(
        ...     Div("content"),
        ...     fluid=True
        ... )  # Full-width container
        >>> container(
        ...     Div(...),
        ...     size="lg",  # 1024px max width
        ...     cls="bg-ui-element-background"
        ... )  # Large container with custom styling
    """

    content: Union[Any, Tuple[Any, ...]]
    fluid: bool = False
    size: ContainerSize = "lg"
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the container."""
        classes = [
            # Base styles
            "grid w-full mx-auto",
        ]

        # Add max-width constraint only if not fluid
        if not self.fluid and self.size in SIZE_CLASSES:
            classes.append(SIZE_CLASSES[self.size])

        # Additional classes
        if self.cls:
            classes.append(self.cls)

        return classes

    def _get_content_elements(self) -> list:
        """Convert content to list if it's a single item."""
        return (
            [self.content]
            if not isinstance(self.content, (list, tuple))
            else list(self.content)
        )

    def __ft__(self) -> Div:
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content_elements = self._get_content_elements()

        return Div(*content_elements, cls=" ".join(filter(None, classes)), **self.attrs)


def container(*content: Any, **kwargs) -> Container:
    """Create a Container instance for responsive layouts.

    This function provides a convenient way to create Container instances with
    smart defaults and multiple child elements.

    Args:
        *content: Variable number of child elements
        **kwargs: Container configuration parameters

    Returns:
        Container: A configured Container instance

    Examples:
        >>> container("content")  # Basic usage with md (768px) width
        >>> container(
        ...     Div(...),
        ...     fluid=True,
        ...     cls="py-lg"
        ... )  # Full-width with padding
        >>> container(
        ...     "header",
        ...     "main",
        ...     size="xl",  # 1280px max width
        ...     cls="space-y-4"
        ... )  # Large container with spacing
    """
    # Separate kwargs into Container params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in CONTAINER_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in CONTAINER_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Container(content, **params)
