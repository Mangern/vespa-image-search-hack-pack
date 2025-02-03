from fasthtml.common import Style, Title

from ...components.grid_background import grid_background
from ...layouts.app_layout import app_layout
from .search_box import homepage_search_box


def register_routes(rt):
    @rt("/")
    def get():
        return (
            Title("Image Search Explorer"),
            grid_background(
                app_layout(
                    Style("main > * { pointer-events: auto; }"),
                    homepage_search_box(),
                    header_attrs={"cls": "bg-transparent border-transparent"},
                    body_attrs={"cls": "grid grid-rows-[minmax(0,1fr)]"},
                    main_attrs={"style": "pointer-events: none;"},
                ),
                content_attrs={"cls": "grid grid-rows-[minmax(0,55px)_minmax(0,1fr)]"},
            ),
        )
