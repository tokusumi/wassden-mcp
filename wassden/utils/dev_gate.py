"""Development feature gate utilities.

This module provides utilities to check if development features are available
and should be enabled based on optional dependencies installation.
"""

import importlib.util


def is_dev_mode() -> bool:
    """Check if development mode is available by verifying optional dev dependencies.

    Returns:
        bool: True if development mode dependencies are installed, False otherwise.
    """
    try:
        # Check for scipy specifically since it's the main blocker for experiment features
        scipy_spec = importlib.util.find_spec("scipy")
        if scipy_spec is None:
            return False

        # Also check for other critical dev packages
        critical_dev_packages = ["pandas", "language_tool_python"]

        for package in critical_dev_packages:
            spec = importlib.util.find_spec(package)
            if spec is None:
                return False

        return True

    except Exception:
        return False
