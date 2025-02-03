from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

from fasthtml.common import Button as BaseButton
from fasthtml.common import Span

from .icon import Icon

ButtonVariant = Literal["default", "filled", "light", "outline", "subtle", "transparent"]
ButtonSize = Literal["xs", "sm", "md", "lg", "xl"]
JustifyContent = Literal["start", "center", "end", "between"]
RadiusSize = Literal["none", "sm", "md", "lg", "xl", "full"]

JUSTIFY_CLASSES: Dict[str, str] = {
    "start": "justify-start",
    "center": "justify-center",
    "end": "justify-end",
    "between": "justify-between",
}

SIZE_CLASSES: Dict[str, str] = {
    "xs": "text-[12px] px-[14px] h-[30px]",
    "sm": "text-[14px] px-[18px] h-[36px]",
    "md": "text-[16px] px-[22px] h-[42px]",
    "lg": "text-[18px] px-[26px] h-[50px]",
    "xl": "text-[20px] px-[32px] h-[60px]",
}

RADIUS_CLASSES: Dict[str, str] = {
    "none": "rounded-none",
    "sm": "rounded-sm",
    "md": "rounded-md",
    "lg": "rounded-lg",
    "xl": "rounded-xl",
    "full": "rounded-full",
}

VARIANT_BASE_CLASSES: Dict[str, str] = {
    "default": "border border-solid-background",
    "filled": "border-transparent",
    "light": "border-transparent",
    "outline": "bg-transparent border",
    "subtle": "bg-transparent border-transparent",
    "transparent": "bg-transparent border-transparent hover:bg-transparent",
}

DEFAULT_COLORS: Dict[str, str] = {
    "default": "bg-subtle-background hover:bg-ui-element-background text-high-contrast-text",
    "filled": "bg-solid-background-green hover:bg-hovered-solid-background-green text-low-contrast-text-berg",
    "light": "bg-ui-element-background-green hover:bg-hovered-ui-element-background-green text-low-contrast-text-green",
    "outline": "border-solid-background-green text-solid-background-green hover:bg-subtle-background-green",
    "subtle": "text-solid-background-green hover:bg-subtle-background-green",
    "transparent": "text-solid-background-green",
}

BUTTON_PARAMS: set[str] = {
    "variant",
    "size",
    "radius",
    "disabled",
    "loading",
    "full_width",
    "justify",
    "left_section",
    "right_section",
    "cls",
}


@dataclass
class Button:
    """A button component with multiple variants and states.

    Args:
        content: Button text content or child elements
        variant: Base button style (affects default styling)
        size: Button size preset (affects padding and font size)
        radius: Border radius preset
        disabled: Disabled state
        loading: Loading state
        full_width: Whether button should take full width
        justify: Content justification
        left_section: Content to show before main content
        right_section: Content to show after main content
        cls: Additional CSS classes for custom styling (colors, hover states, etc.)
        attrs: Additional HTML attributes

    Examples:
        >>> button(
        ...     "Submit",
        ...     variant="filled",
        ...     cls="bg-solid-background-blue hover:bg-hovered-solid-background-blue text-low-contrast-text-berg"
        ... )

        >>> button(
        ...     "Delete",
        ...     variant="outline",
        ...     left_section=Icon("trash"),
        ...     cls="border-solid-background-red text-solid-background-red hover:bg-hovered-subtle-background-red"
        ... )
    """

    content: Any
    variant: ButtonVariant = "filled"
    size: ButtonSize = "sm"
    radius: RadiusSize = "sm"
    disabled: bool = False
    loading: bool = False
    full_width: bool = False
    justify: JustifyContent = "center"
    left_section: Optional[Any] = None
    right_section: Optional[Any] = None
    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    def _get_base_classes(self) -> list[str]:
        """Get the base classes for the button."""
        return [
            # Base styles
            "inline-grid grid-flow-col items-center font-semibold transition-colors duration-200",
            # Size classes
            SIZE_CLASSES[self.size],
            # Radius
            RADIUS_CLASSES.get(self.radius, "rounded-sm"),
            # Justify content
            JUSTIFY_CLASSES[self.justify],
            # Base variant class (without colors)
            VARIANT_BASE_CLASSES[self.variant],
            # Full width
            "w-full" if self.full_width else "",
            # Disabled/Loading states
            "opacity-50 cursor-not-allowed pointer-events-none"
            if self.disabled or self.loading
            else "",
            # Additional classes (including colors)
            self.cls or "",
        ]

    def _get_content_elements(self) -> list:
        """Build the content elements for the button."""
        elements = []

        # Add left section if provided
        if self.left_section:
            elements.append(Span(self.left_section, cls="-ml-0.5 mr-1.5"))

        # Add main content
        elements.append(self.content)

        # Add right section if provided
        if self.right_section:
            elements.append(Span(self.right_section, cls="ml-1.5 -mr-0.5"))

        # Handle loading state
        if self.loading:
            return [
                Span(
                    Icon("spinner", animation="spin"),
                    cls="absolute inset-0 flex items-center justify-center",
                ),
                Span(*elements, cls="invisible"),
            ]

        return elements

    def __ft__(self) -> BaseButton:
        """Convert to FastHTML FT component."""
        classes = self._get_base_classes()
        content_elements = self._get_content_elements()

        if self.loading:
            classes.append("relative")

        button_attrs = {
            "type": "button",
            "disabled": self.disabled or self.loading,
            **self.attrs,
        }

        return BaseButton(
            *content_elements, cls=" ".join(filter(None, classes)), **button_attrs
        )


def button(content: Any, **kwargs) -> Button:
    """Create a Button instance with smart color handling.

    This function provides a convenient way to create Button instances with automatic
    color management based on variants, while allowing custom color overrides.

    Args:
        content: The button's content
        **kwargs: Button configuration parameters

    Returns:
        Button: A configured Button instance

    Examples:
        >>> button("Click me", variant="filled")  # Uses default variant colors
        >>> button("Submit", variant="outline", cls="border-blue-500")  # Custom colors
    """
    variant = kwargs.get("variant", "filled")
    variant_colors = DEFAULT_COLORS[variant]

    if "cls" in kwargs:
        custom_classes = kwargs["cls"]
        # Check if custom classes contain color utilities
        has_colors = any(
            cls.startswith(("bg-", "text-", "hover:bg-"))
            for cls in custom_classes.split()
        )
        kwargs["cls"] = (
            custom_classes if has_colors else f"{variant_colors} {custom_classes}"
        )
    else:
        kwargs["cls"] = variant_colors

    # Separate kwargs into Button params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in BUTTON_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in BUTTON_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return Button(content, **params)
