import logging

from fasthtml.common import Div, Input

from ...components.grid_background import GridManager

logger = logging.getLogger(__name__)


def register_routes(rt):
    grid_manager = GridManager()

    @rt("/api/grid-images")
    async def get_grid_images(req):
        """Generate a grid of images optimized for the current viewport."""
        try:
            # Get query parameters with defaults
            params = req.query_params
            width_param = params.get("viewport-width", "1920")
            height_param = params.get("viewport-height", "1080")

            # Validate and constrain dimensions
            if not width_param.isdigit() or not height_param.isdigit():
                raise ValueError("Invalid viewport dimensions")

            viewport_width = max(320, min(int(width_param), 3840))
            viewport_height = max(240, min(int(height_param), 2160))

            logger.info(
                f"Validated viewport dimensions: {viewport_width}x{viewport_height}"
            )

        except (TypeError, ValueError) as e:
            # Fallback to default dimensions on error
            logger.error(f"Error with viewport dimensions: {e}")
            viewport_width = 1920
            viewport_height = 1080

        try:
            # Create grid cells and layout variables
            cells, layout_vars = grid_manager.create_grid_cells(
                viewport_width, viewport_height
            )

            if not cells:
                # Return an empty grid background if no cells are generated
                return Div(cls="grid-background")

            # Generate style string from layout variables
            style_str = "; ".join(f"{k}: {v}" for k, v in layout_vars.items())

            # Return the grid with hidden inputs and cells
            return Div(
                Div(
                    Input(
                        type="hidden",
                        name="viewport-width",
                        id="viewport-width",
                        value=str(viewport_width),
                    ),
                    Input(
                        type="hidden",
                        name="viewport-height",
                        id="viewport-height",
                        value=str(viewport_height),
                    ),
                    cls="hidden",
                ),
                *cells,
                style=style_str,
                cls="grid-background",
            )

        except Exception as e:
            # Log unexpected errors and return a minimal fallback grid
            logger.error(f"Unexpected error generating grid: {e}")
            fallback_style = "--cell-size: 89px; --column-count: 8; --row-count: 6"
            return Div(
                cls="grid-background",
                style=fallback_style,
            )
