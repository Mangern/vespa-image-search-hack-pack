from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Literal, Optional, Sequence, Set

from fasthtml.common import Div, Label, P, Span
from fasthtml.common import Input as BaseInput

InputVariant = Literal["default", "filled", "unstyled"]
InputSize = Literal["xs", "sm", "md", "lg", "xl"]
InputRadius = Literal["none", "sm", "md", "lg", "xl", "full"]
InputOrder = Literal["input", "label", "description", "error"]

SIZE_CLASSES: Dict[str, str] = {
    "xs": "h-[30px] text-xs",
    "sm": "h-[36px] text-sm",
    "md": "h-[42px] text-md",
    "lg": "h-[42px] text-md sm:h-[50px] sm:text-lg",
    "xl": "h-[60px] text-xl",
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
    "default": "bg-app-background",
    "filled": "bg-ui-element-background",
    "unstyled": "bg-transparent",
}

DEFAULT_INPUT_ORDER: list[InputOrder] = ["label", "description", "input", "error"]

TEXT_INPUT_PARAMS: Set[str] = {
    "description",
    "disabled",
    "error",
    "input_size",
    "input_wrapper_order",
    "label",
    "left_section",
    "pointer",
    "radius",
    "required",
    "right_section",
    "size",
    "with_asterisk",
    "with_error_styles",
    "with_focus",
    "variant",
    "cls",
}


@dataclass
class TextInput:
    """A text input component with multiple variants and states.

    Creates a form input with support for labels, descriptions, error states,
    and various visual styles.

    Args:
        content: Input content/value
        description: Description shown below the label
        disabled: Sets disabled attribute
        error: Error message content
        input_size: Size of input element
        input_wrapper_order: Controls element order
        label: Label content
        left_section: Content for left section
        pointer: Whether to show pointer cursor
        radius: Border radius setting
        required: Add required attribute and asterisk
        right_section: Content for right section
        size: Controls input height and padding
        with_asterisk: Show asterisk without required
        with_error_styles: Show error styling with error
        with_focus: Show focus ring and border styles
        variant: Visual style variant
        cls: Additional CSS classes
        attrs: Additional HTML attributes

    Examples:
        >>> text_input(label="Username")  # Simple input
        >>> text_input(
        ...     label="Email",
        ...     description="Work email preferred",
        ...     required=True,
        ...     size="lg"
        ... )  # Complex input
    """

    content: Any = None
    description: Optional[Any] = None
    disabled: bool = False
    error: Optional[Any] = None
    input_size: InputSize = "sm"
    input_wrapper_order: Sequence[InputOrder] = field(
        default_factory=lambda: list(DEFAULT_INPUT_ORDER)
    )
    label: Optional[Any] = None
    left_section: Optional[Any] = None
    pointer: bool = False
    radius: InputRadius = "sm"
    required: bool = False
    right_section: Optional[Any] = None
    size: InputSize = "sm"
    with_asterisk: bool = False
    with_error_styles: bool = True
    with_focus: bool = True
    variant: InputVariant = "default"
    cls: Optional[str] = None
    attrs: dict = field(default_factory=dict)

    @staticmethod
    def _get_wrapper_classes() -> list[str]:
        """Get classes for the outer wrapper element."""
        return ["flex flex-col gap-1", "w-full"]

    def _get_input_container_classes(self) -> list[str]:
        """Get classes for the input container."""
        has_error = self.error and self.with_error_styles
        has_left = bool(self.left_section)
        has_right = bool(self.right_section)

        grid_cols = {
            (True, True): "grid-cols-[max-content_1fr_max-content]",  # both sections
            (True, False): "grid-cols-[max-content_1fr]",  # left only
            (False, True): "grid-cols-[1fr_max-content]",  # right only
            (False, False): "grid-cols-1",  # no sections
        }

        # Define focus styles based on with_focus prop
        focus_styles = (
            "focus-within:ring-2 focus-within:ring-high-contrast-text focus-within:border-ui-element-border-and-focus"
            if self.with_focus
            else "focus-within:ring-transparent focus-within:border-transparent"
        )

        return [
            # Base styles
            "grid items-center transition-colors duration-200",
            # Grid columns based on sections
            grid_cols[(has_left, has_right)],
            # Gap between sections
            "gap-0" if (has_left or has_right) else "",
            # Padding when no sections
            "px-md" if not (has_left or has_right) else "",
            # Padding when only one section
            "pr-md" if has_left and not has_right else "",
            "pl-md" if has_right and not has_left else "",
            # Size classes
            SIZE_CLASSES[self.size],
            # Radius
            RADIUS_CLASSES[self.radius],
            # Variant styling
            VARIANT_BASE_CLASSES[self.variant],
            # Border styling
            "border border-ui-element-border-and-focus hover:border-hovered-ui-element-border"
            if self.variant == "default"
            else "",
            # Focus styling
            focus_styles,
            # Error styles
            "!border-solid-background-red focus-within:!ring-solid-background-red focus-within:!border-solid-background-red"
            if has_error
            else "",
            # Disabled state
            "opacity-50 cursor-not-allowed pointer-events-none" if self.disabled else "",
            # Pointer
            "cursor-pointer" if self.pointer else "",
            # Additional classes
            self.cls or "",
        ]

    def _get_input_classes(self) -> list[str]:
        """Get classes for the input element."""
        has_error = self.error and self.with_error_styles

        return [
            # Base styles
            "w-full bg-transparent outline-none min-w-0",
            # Error text color
            "text-solid-background-red placeholder-solid-background-red/50"
            if has_error
            else "",
            # States
            "cursor-not-allowed" if self.disabled else "",
            "cursor-pointer" if self.pointer else "",
        ]

    def _create_ordered_elements(self) -> Dict[str, Callable[[], Optional[Any]]]:
        """Create a mapping of element creators."""
        return {
            "label": lambda: Label(
                self.label,
                Span(" *", cls="text-solid-background-red ml-1")
                if (self.required or self.with_asterisk) and self.label
                else None,
                cls="text-sm font-medium",
            )
            if self.label
            else None,
            "description": lambda: P(
                self.description, cls="text-xs text-low-contrast-text"
            )
            if self.description
            else None,
            "input": lambda: Div(
                Div(
                    self.left_section,
                    cls="px-md flex items-center justify-center text-low-contrast-text",
                )
                if self.left_section
                else None,
                BaseInput(
                    value=self.content if isinstance(self.content, str) else None,
                    cls=" ".join(filter(None, self._get_input_classes())),
                    required=self.required and not self.with_asterisk,
                    disabled=self.disabled,
                    **self.attrs,
                ),
                Div(
                    self.right_section,
                    cls="px-md flex items-center justify-center text-low-contrast-text",
                )
                if self.right_section
                else None,
                cls=" ".join(filter(None, self._get_input_container_classes())),
            ),
            "error": lambda: P(self.error, cls="text-xs text-solid-background-red")
            if self.error
            else None,
        }

    def _get_elements(self) -> list:
        """Get all elements in the correct order."""
        ordered_elements = self._create_ordered_elements()
        elements = []

        for element_type in self.input_wrapper_order:
            if element := ordered_elements[element_type]():
                elements.append(element)

        return elements

    def __ft__(self) -> Div:
        """Convert to FastHTML FT component."""
        wrapper_classes = self._get_wrapper_classes()
        elements = self._get_elements()

        return Div(*elements, cls=" ".join(filter(None, wrapper_classes)))


def text_input(content: Any = None, **kwargs) -> TextInput:
    """Create a TextInput instance with smart parameter handling.

    This function provides a convenient way to create TextInput instances
    with support for labels, descriptions, and various visual styles.

    Args:
        content: The input's initial content
        **kwargs: TextInput configuration parameters

    Returns:
        TextInput: A configured TextInput instance

    Examples:
        >>> text_input("Initial value")  # With value
        >>> text_input(
        ...     label="Password",
        ...     right_section=Div("icon-eye"),
        ...     variant="filled"
        ... )  # Complex setup
        >>> text_input(
        ...     label="Search",
        ...     with_focus=False,  # Disable focus styles
        ...     variant="unstyled"
        ... )  # Input without focus effects
    """
    # Separate kwargs into TextInput params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in TEXT_INPUT_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in TEXT_INPUT_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return TextInput(content, **params)
