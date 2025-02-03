"""Routes package initialization.

This module automatically discovers and registers all routes from the views and api packages.
"""

import importlib
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import List


def discover_route_modules(package: ModuleType) -> List[ModuleType]:
    """Discover all route modules within a package."""
    modules = []
    # Get the package's directory path
    pkg_path = Path(package.__file__).parent

    # Walk through all modules in the package
    for _, name, _ in pkgutil.iter_modules([str(pkg_path)]):
        # Import the module
        module = importlib.import_module(f"{package.__name__}.{name}")
        # Check if module has register_routes function
        if hasattr(module, "register_routes"):
            modules.append(module)

    return modules


def register_routes(rt):
    """Register all application routes automatically."""
    from . import api, views

    # Discover and register view routes
    for module in discover_route_modules(views):
        module.register_routes(rt)

    # Discover and register API routes
    for module in discover_route_modules(api):
        module.register_routes(rt)
