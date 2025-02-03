"""Views package initialization.

This package contains all view routes that render HTML pages.
Each module in this package should define a register_routes function.
Routes are automatically discovered and registered from this package.

Example route module:
    def register_routes(rt):
        @rt("/path")
        def get():
            return Component()
"""

# This file can be empty because we're using automatic discovery
# The docstring is just for documentation purposes
