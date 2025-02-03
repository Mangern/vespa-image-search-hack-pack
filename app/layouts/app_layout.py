from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, Tuple, Union

from ..components.group import group
from ..components.icon import social_icon
from ..components.link import link
from .body import body
from .header import header
from .layout import layout
from .logo import logo
from .main import main
from .nav import nav
from .theme_toggle import theme_toggle
from .toolbar import toolbar

# Constants
APPLAYOUT_PARAMS: Set[str] = {
    "is_home",
    "navigation_items",
    "left_sidebar",
    "right_sidebar",
    "with_toolbar",
    "toolbar_attrs",
    "header_attrs",
    "layout_attrs",
    "body_attrs",
    "main_attrs",
    "nav_attrs",
}

# Grid row template constants
GRID_ROWS = {
    "default": "grid-rows-[minmax(0,55px)_minmax(0,1fr)]",
    "with_toolbar": "grid-rows-[minmax(0,55px)_max-content_minmax(0,1fr)]",
}

DEFAULT_NAV_ITEMS = (
    link(
        social_icon("x-twitter", size="lg", cls="text-high-contrast-text"),
        to="https://x.com/vespaengine",
    ),
    link(
        social_icon("github", size="lg", cls="text-high-contrast-text"),
        to="https://github.com/vespa-engine",
    ),
    link(
        social_icon("linkedin", size="lg", cls="text-high-contrast-text"),
        to="https://www.linkedin.com/company/vespa-ai",
    ),
    link(
        social_icon("youtube", size="lg", cls="text-high-contrast-text"),
        to="https://youtube.com/@vespaai",
    ),
    link(
        social_icon("slack", size="lg", cls="text-high-contrast-text"),
        to="https://slack.vespa.ai",
    ),
    social_icon("discord", size="lg", cls="text-high-contrast-text"),
)


@dataclass
class AppLayout:
    """Pre-configured application layout combining all base layout components.

    A high-level layout component that provides a complete application structure
    with header, optional toolbar, navigation, optional sidebars, and main content area.

    Args:
        content: Main content area elements. Can be single item or tuple/list.
        is_home: Whether this is the home page layout
        navigation_items: Additional items to be displayed in the header navigation
                        (Will be combined with default social icons)
        left_sidebar: Optional left sidebar content
        right_sidebar: Optional right sidebar content
        with_toolbar: Whether to include a toolbar below the header
        header_attrs: Additional attributes for the header
        toolbar_attrs: Additional attributes for the toolbar (including toolbar content)
        layout_attrs: Additional attributes for the layout
        body_attrs: Additional attributes for the body
        main_attrs: Additional attributes for the main content
        nav_attrs: Additional attributes for the navigation
        attrs: Additional HTML attributes
    """

    content: Union[Any, Tuple[Any, ...]]
    is_home: bool = False
    navigation_items: Optional[Tuple[Any, ...]] = None
    left_sidebar: Optional[Any] = None
    right_sidebar: Optional[Any] = None
    with_toolbar: bool = False
    header_attrs: Dict = field(default_factory=dict)
    toolbar_attrs: Dict = field(default_factory=dict)
    layout_attrs: Dict = field(default_factory=dict)
    body_attrs: Dict = field(default_factory=dict)
    main_attrs: Dict = field(default_factory=dict)
    nav_attrs: Dict = field(default_factory=dict)
    attrs: Dict = field(default_factory=dict)

    def _get_content_elements(self) -> list:
        """Convert content to a list if it's a single item."""
        return (
            [self.content]
            if not isinstance(self.content, (list, tuple))
            else list(self.content)
        )

    def _create_header_content(self) -> Tuple[Any, ...]:
        """Create the header content with logo, nav, and theme toggle."""
        # Create the app logo
        app_logo = link(logo(cls="h-[25px]"), to="/")

        # Combine custom navigation items with default social icons
        all_nav_items = self.navigation_items or ()
        nav_items = (*all_nav_items, *DEFAULT_NAV_ITEMS)

        # Create navigation with theme toggle
        right_section = group(
            nav(*nav_items, **self.nav_attrs), theme_toggle(), cls="gap-sm md:gap-lg"
        )

        return app_logo, right_section

    def _create_body_content(self, main_content: list) -> Tuple[Any, ...]:
        """Create the body content with header, toolbar if enabled, sidebars, and main content."""
        body_items = []

        # Add header
        header_content = self._create_header_content()
        body_items.append(
            header(*header_content, is_home=self.is_home, **self.header_attrs)
        )

        # Add toolbar if enabled
        if self.with_toolbar:
            body_items.append(toolbar(**self.toolbar_attrs))

        # Add left sidebar if provided
        if self.left_sidebar:
            body_items.append(self.left_sidebar)

        # Add main content
        body_items.append(main(*main_content, **self.main_attrs))

        # Add right sidebar if provided
        if self.right_sidebar:
            body_items.append(self.right_sidebar)

        return tuple(body_items)

    def __ft__(self):
        """Convert to FastHTML FT component."""
        content = self._get_content_elements()
        body_content = self._create_body_content(content)

        # Prepare body attributes with appropriate grid rows template
        body_grid = (
            GRID_ROWS["with_toolbar"] if self.with_toolbar else GRID_ROWS["default"]
        )
        body_attrs = {
            **{"cls": f"grid {body_grid}"},  # Base grid classes first
            **self.body_attrs,  # Then any custom attributes which may include additional classes
        }

        # Create the complete layout
        return layout(
            body(*body_content, is_home=self.is_home, **body_attrs),
            **self.layout_attrs,
            **self.attrs,
        )


def app_layout(*content: Any, **kwargs) -> AppLayout:
    """Create an AppLayout instance with smart parameter handling.

    This function provides a convenient way to create AppLayout instances
    with all required layout components pre-configured.

    Args:
        *content: Variable number of child elements for the main content area
        **kwargs: AppLayout configuration parameters including:
            - with_toolbar: Enable toolbar below header
            - toolbar_attrs: Attributes and content for the toolbar

    Returns:
        AppLayout: A configured AppLayout instance
    """
    # Separate kwargs into AppLayout params and HTML attributes
    params = {k: v for k, v in kwargs.items() if k in APPLAYOUT_PARAMS}
    attrs = {k: v for k, v in kwargs.items() if k not in APPLAYOUT_PARAMS}

    if attrs:
        params["attrs"] = attrs

    return AppLayout(content, **params)
