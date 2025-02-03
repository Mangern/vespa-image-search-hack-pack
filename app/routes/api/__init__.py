"""API package initialization.

This package contains all API routes that handle data operations.
Each module in this package should define a register_routes function.
Routes are automatically discovered and registered from this package.

Example route module:
    def register_routes(rt):
        @rt("/api/data")
        def get():
            return {"data": "value"}

        @rt("/api/data")
        def post(data: dict):
            return {"status": "created"}
"""

# This file can be empty because we're using automatic discovery
# The docstring is just for documentation purposes
