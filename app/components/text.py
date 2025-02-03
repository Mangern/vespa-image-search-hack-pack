from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Set, Union

from fasthtml.common import P, Span

TextSize = Literal["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"]
LineClamp = Literal[1, 2, 3, 4, 5, 6, "none"]

SIZE_CLASSES: Dict[str, str] = {
    "xs": "text-xs leading-normal",
    "sm": "text-sm leading-normal",
    "md": "text-base leading-normal",
    "lg": "text-lg leading-normal",
    "xl": "text-xl leading-normal",
    "2xl": "text-2xl leading-normal",
    "3xl": "text-3xl leading-normal",
    "4xl": "text-4xl leading-normal",
}

LINE_CLAMP_CLASSES: Dict[Union[int, str], str] = {
    1: "line-clamp-1",
    2: "line-clamp-2",
    3: "line-clamp-3",
    4: "line-clamp-4",
    5: "line-clamp-5",
    6: "line-clamp-6",
    "none": "line-clamp-none",
}

TEXT_PARAMS: Set[str] = {
    "inherit",
    "inline",
    "line_clamp",
    "size",
    "span",
    "truncate",
    "cls",
}


@dataclass
class Text:
    """A text component with rich typography controls.

    Creates a text element with customizable typography, truncation,
    and layout options.

    Args:
        content: Text content to display
        inherit: Whether font properties should inherit from parent
        inline: Sets line-height to 1 for centering
        line_clamp: Number of lines before truncation
        size: Font size preset
        span: Use span instead of p element
        truncate: Enable text truncation with ellipsis
        cls: Additional CSS classes
        attrs: Additional HTML attributes

    Examples:
        >>> text("Hello world", size="lg")  # Large text
        >>> text(
        ...     "Long text that might need truncating...",
        ...     line_clamp=2,
        ...     size="sm"
        ... )  # Truncated small text
    """

    content: Any
    inherit: bool = False
    inline: bool = False
    line_clamp: Optional[LineClamp] = None
    size: TextSize = "md"
    span: bool = False
    truncate: bool = False
    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the text element."""
        return [
            # Font size and line height
            "" if self.inherit else SIZE_CLASSES[self.size],
            # Line height adjustment for inline
            "leading-none" if self.inline else "",
            # Line clamp
            LINE_CLAMP_CLASSES[self.line_clamp] if self.line_clamp else "",
            # Truncate
            "truncate" if self.truncate else "",
            # Additional classes
            self.cls or "",
        ]

    def __ft__(self) -> Union[P, Span]:
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        element_type = Span if self.span else P

        return element_type(
            self.content, cls=" ".join(filter(None, classes)), **self.attrs
        )


def text(content: Any, **kwargs) -> Text:
    """Create a Text instance with smart typography controls.

    This function provides a convenient way to create Text instances with
    configurable typography and layout options.

    Args:
        content: The text content
        **kwargs: Text configuration parameters

    Returns:
        Text: A configured Text instance

    Examples:
        >>> text("Regular text")  # Basic usage
        >>> text("Title", size="2xl", span=True)  # Large inline text
        >>> text(
        ...     "Long description...",
        ...     line_clamp=3,
        ...     cls="italic"
        ... )  # Truncated with styling
    """

    # Separate kwargs into Text params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in TEXT_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in TEXT_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Text(content, **params)
