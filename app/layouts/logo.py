from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from fasthtml.common import Div, Img

LOGO_PATHS: Dict[str, str] = {
    "light": "/app/static/img/vespa-logo-black.svg",
    "dark": "/app/static/img/vespa-logo-white.svg",
}

LOGO_PARAMS: Set[str] = {"cls"}


@dataclass
class Logo:
    """Logo component that handles both light and dark mode variants.

    Creates a container with two logo variants, automatically switching
    between them based on the user's color scheme preference.

    Args:
        cls: Additional CSS classes for the container
        attrs: Additional HTML attributes for the container

    Examples:
        >>> logo()  # Basic usage
        >>> logo(cls="w-32")  # With custom width
        >>> logo(cls="h-8 hover:opacity-80")  # With hover effect
    """

    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    @staticmethod
    def _create_logo_image(mode: str, show_in_dark: bool) -> Img:
        """Create a logo image element for the specified mode.

        Args:
            mode: Either "light" or "dark"
            show_in_dark: Whether this variant shows in dark mode

        Returns:
            Img: A configured logo image element
        """
        return Img(
            src=LOGO_PATHS[mode],
            alt="Vespa Logo",
            cls=f"h-full {'hidden dark:block' if show_in_dark else 'dark:hidden'}",
        )

    def _get_logo_variants(self) -> list:
        """Get both logo variants for light/dark modes."""
        return [
            self._create_logo_image("light", False),  # Light mode logo
            self._create_logo_image("dark", True),  # Dark mode logo
        ]

    def __ft__(self) -> Div:
        """Convert to FastHTML FT component."""
        return Div(*self._get_logo_variants(), cls=self.cls, **self.attrs)


def logo(**kwargs) -> Logo:
    """Create a Logo instance with smart parameter handling.

    This function provides a convenient way to create Logo instances while
    properly separating component parameters from HTML attributes.

    Args:
        **kwargs: Logo configuration parameters and HTML attributes

    Returns:
        Logo: A configured Logo instance

    Examples:
        >>> logo()  # Default usage
        >>> logo(cls="w-40 h-10")  # Custom size
        >>> logo(
        ...     cls="h-6",
        ...     role="banner"  # Role will be passed as an HTML attribute
        ... )
    """
    # Separate kwargs into Logo params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in LOGO_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in LOGO_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Logo(**params)
