from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Set, Union

from fasthtml.common import A

LinkSize = Literal["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"]
UnderlineType = Literal["always", "hover", "never"]
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

UNDERLINE_CLASSES: Dict[str, str] = {
    "always": "underline",
    "hover": "no-underline hover:underline",
    "never": "no-underline",
}

LINK_PARAMS: Set[str] = {
    "to",
    "inherit",
    "inline",
    "line_clamp",
    "size",
    "truncate",
    "underline",
    "cls",
}


@dataclass
class Link:
    """A link component with rich typography and interaction controls.

    Creates a link element with customizable typography, truncation,
    and external link handling.

    Args:
        content: Link text content or child elements
        to: URL for the link
        inherit: Whether font properties should inherit from parent
        inline: Sets line-height to 1 for centering
        line_clamp: Number of lines after which text will be truncated
        size: Font size preset
        truncate: Enable text truncation with ellipsis
        underline: Controls text decoration behavior
        cls: Additional CSS classes
        attrs: Additional HTML attributes

    Examples:
        >>> link("Documentation", to="/docs", size="lg")
        >>> link(
        ...     "External Site",
        ...     to="https://example.com",
        ...     underline="always"
        ... )
        >>> link(
        ...     "Long title...",
        ...     to="/article",
        ...     truncate=True,
        ...     line_clamp=2
        ... )
    """

    content: Any
    to: str
    inherit: bool = False
    inline: bool = False
    line_clamp: Optional[LineClamp] = None
    size: LinkSize = "md"
    truncate: bool = False
    underline: UnderlineType = "hover"
    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    def _is_external_url(self) -> bool:
        """Check if the URL is external."""
        return self.to.startswith(("http://", "https://"))

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the link."""
        return [
            # Base styles
            "text-solid-background-blue hover:text-hovered-solid-background-blue transition-colors duration-200",
            # Font size and line height
            "" if self.inherit else SIZE_CLASSES[self.size],
            # Line height adjustment for inline
            "leading-none" if self.inline else "",
            # Line clamp
            LINE_CLAMP_CLASSES[self.line_clamp] if self.line_clamp else "",
            # Truncate
            "truncate" if self.truncate else "",
            # Underline behavior
            UNDERLINE_CLASSES[self.underline],
            # Additional classes
            self.cls or "",
        ]

    def _prepare_attributes(self) -> dict:
        """Prepare the HTML attributes for the link."""
        attrs = self.attrs.copy()

        # Add external link attributes if needed
        if self._is_external_url():
            attrs.update(
                {
                    "target": "_blank",
                    "rel": "noopener noreferrer",
                }
            )

        # Always set href
        attrs["href"] = self.to

        return attrs

    def __ft__(self) -> A:
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        attrs = self._prepare_attributes()

        return A(self.content, cls=" ".join(filter(None, classes)), **attrs)


def link(content: Any, **kwargs) -> Link:
    """Create a Link instance with smart parameter handling.

    This function provides a convenient way to create Link instances while
    properly separating component parameters from HTML attributes.

    Args:
        content: The link content
        **kwargs: Link configuration parameters and HTML attributes

    Returns:
        Link: A configured Link instance

    Examples:
        >>> link("Home", to="/")  # Basic usage
        >>> link(
        ...     "Read more",
        ...     to="/article",
        ...     size="lg",
        ...     underline="always"
        ... )  # Advanced usage
    """

    # Separate kwargs into Link params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in LINK_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in LINK_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Link(content, **params)
