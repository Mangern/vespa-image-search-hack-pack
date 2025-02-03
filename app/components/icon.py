from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Set

from fasthtml.common import I

IconSize = Literal["2xs", "xs", "sm", "lg", "xl", "2xl"]
IconType = Literal["solid", "regular", "brands", "light", "thin", "duotone"]
IconAnimation = Literal["spin", "pulse", "shake", "beat", "fade", "flip", "bounce"]

TYPE_MAP: Dict[str, IconType] = {
    "fas": "solid",
    "far": "regular",
    "fab": "brands",
    "fal": "light",
    "fat": "thin",
    "fad": "duotone",
}

ICON_PARAMS: Set[str] = {
    "type",
    "size",
    "animation",
    "disabled",
    "cls",
}


@dataclass
class Icon:
    """A FontAwesome icon component for FastHTML.

    Creates an icon element using FontAwesome classes with support for
    different styles, sizes, animations and states.

    Args:
        name: Icon name without 'fa-' prefix
        type: Icon type/style
        size: Icon size modifier
        animation: Animation effect
        disabled: Apply disabled styling
        cls: Additional CSS classes for colors and customization
        attrs: Additional HTML attributes

    Examples:
        >>> icon("home")  # Basic usage
        >>> icon(
        ...     "star",
        ...     cls="text-solid-background-yellow"
        ... )  # With semantic color
        >>> icon(
        ...     "spinner",
        ...     animation="spin",
        ...     cls="text-solid-background-blue"
        ... )  # Animated
    """

    name: str
    type: IconType = "solid"
    size: Optional[IconSize] = None
    animation: Optional[IconAnimation] = None
    disabled: bool = False
    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    def _resolve_name(self) -> str:
        """Convert shorthand notation to full name and update type if needed."""
        prefixes = [f"{k}-" for k in TYPE_MAP]
        if any(self.name.startswith(prefix) for prefix in prefixes):
            prefix = self.name[:3]
            if prefix in TYPE_MAP:
                self.type = TYPE_MAP[prefix]
                return self.name[4:]
        return self.name

    def _get_base_classes(self, resolved_name: str) -> list[str]:
        """Get the base classes for the icon."""
        return [
            # Base icon classes
            f"fa-{self.type}",
            f"fa-{resolved_name}",
            # Optional modifiers
            f"fa-{self.size}" if self.size else "",
            f"fa-{self.animation}" if self.animation else "",
            # Disabled state
            "opacity-50 cursor-not-allowed" if self.disabled else "",
            # Additional classes for colors and customization
            self.cls or "",
        ]

    def __ft__(self) -> I:
        """Convert to FastHTML FT component."""
        resolved_name = self._resolve_name()
        classes = self._get_base_classes(resolved_name)

        return I(cls=" ".join(filter(None, classes)), **self.attrs)


def icon(name: str, **kwargs) -> Icon:
    """Create an Icon instance with smart parameter handling.

    This function provides a convenient way to create Icon instances while
    properly separating component parameters from HTML attributes.

    Args:
        name: The icon name
        **kwargs: Icon configuration parameters and HTML attributes

    Returns:
        Icon: A configured Icon instance

    Examples:
        >>> icon("star", size="lg")  # Large star icon
        >>> icon(
        ...     "check",
        ...     animation="bounce",
        ...     cls="text-solid-background-green"
        ... )  # Animated checkmark
    """
    # Separate kwargs into Icon params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in ICON_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in ICON_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Icon(name, **params)


def social_icon(name: str, **kwargs) -> Icon:
    """Create a branded social media icon.

    Args:
        name: Brand icon name (e.g. "github", "twitter")
        **kwargs: Additional icon parameters

    Examples:
        >>> social_icon("github")
        >>> social_icon("twitter", size="lg")
    """
    return icon(name, type="brands", **kwargs)


def regular_icon(name: str, **kwargs) -> Icon:
    """Create an icon using the regular (outlined) style.

    Args:
        name: Icon name
        **kwargs: Additional icon parameters

    Examples:
        >>> regular_icon("user")
        >>> regular_icon("heart", size="lg")
    """
    return icon(name, type="regular", **kwargs)
