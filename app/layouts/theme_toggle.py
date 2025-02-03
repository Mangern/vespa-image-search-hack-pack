from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Set

from fasthtml.common import Button as BaseButton

from ..components.icon import icon

# Type definitions
ThemeToggleSize = Literal["sm", "md", "lg", "xl"]

# Constants
THEME_TOGGLE_PARAMS: Set[str] = {
    "size",
    "cls",
}

CLASS_GROUPS: Dict[str, str] = {
    "base": "theme-toggle rounded-full flex items-center justify-center",
    "theme": "bg-ui-element-background hover:bg-hovered-ui-element-background",
    "animation": "transition-colors duration-200",
}

SIZE_CLASSES: Dict[str, str] = {
    "sm": "h-6 w-6",
    "md": "h-8 w-8",
    "lg": "h-10 w-10",
    "xl": "h-12 w-12",
}

ICON_VARIANTS: Dict[str, Dict[str, str]] = {
    "light": {
        "name": "moon",
        "cls": "text-solid-background-berg block dark:hidden",
    },
    "dark": {
        "name": "sun",
        "cls": "hidden text-solid-background-amber dark:block",
    },
}


@dataclass
class ThemeToggle:
    """Theme toggle component for switching between light and dark modes.

    Creates a button that toggles between light and dark themes with
    appropriate icons and transitions. Handles theme switching via CSS
    classes and provides smooth transitions.

    Args:
        size: Button size preset (sm through xl)
        cls: Additional CSS classes for custom styling
        attrs: Additional HTML attributes

    Examples:
        >>> # Basic usage
        >>> theme_toggle()

        >>> # Custom size and positioning
        >>> theme_toggle(
        ...     size="lg",
        ...     cls="absolute top-4 right-4"
        ... )
    """

    size: ThemeToggleSize = "md"
    cls: Optional[str] = None
    attrs: Dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the theme toggle button."""
        return [
            # Size variant
            SIZE_CLASSES[self.size],
            # Grouped classes for better organization
            CLASS_GROUPS["base"],
            CLASS_GROUPS["theme"],
            CLASS_GROUPS["animation"],
            # Additional custom classes
            self.cls or "",
        ]

    @staticmethod
    def _get_theme_icons() -> List[icon]:
        """Get the icons for both light and dark themes."""
        return [
            icon(ICON_VARIANTS["light"]["name"], cls=ICON_VARIANTS["light"]["cls"]),
            icon(ICON_VARIANTS["dark"]["name"], cls=ICON_VARIANTS["dark"]["cls"]),
        ]

    def __ft__(self) -> BaseButton:
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        icons = self._get_theme_icons()

        return BaseButton(
            *icons,
            cls=" ".join(filter(None, classes)),
            **self.attrs,
        )


def theme_toggle(**kwargs) -> ThemeToggle:
    """Create a ThemeToggle instance with smart parameter handling.

    This function provides a convenient way to create ThemeToggle instances with
    multiple configuration options.

    Args:
        **kwargs: ThemeToggle configuration parameters

    Returns:
        ThemeToggle: A configured ThemeToggle instance

    Examples:
        >>> # Basic usage
        >>> theme_toggle()

        >>> # Custom size and positioning
        >>> theme_toggle(
        ...     size="xl",
        ...     cls="fixed bottom-4 right-4"
        ... )
    """
    # Separate kwargs into ThemeToggle params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in THEME_TOGGLE_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in THEME_TOGGLE_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return ThemeToggle(**params)
