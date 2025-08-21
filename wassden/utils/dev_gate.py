"""Development feature gate utilities.

This module provides utilities to check if development features are available
and should be enabled based on optional dependencies installation.
"""

import importlib.util
from importlib import metadata


def is_dev_mode() -> bool:
    """Check if development mode is available by verifying optional dev dependencies.

    Returns:
        bool: True if development mode dependencies are installed, False otherwise.
    """
    try:
        # Check for dev-specific packages that are only installed with [dev]
        dev_packages = ["language-tool-python", "pandas", "rich"]

        for package in dev_packages:
            try:
                importlib.util.find_spec(package)
            except (ImportError, AttributeError, ValueError):
                return False

        # Additional check: verify wassden was installed with [dev] extra
        try:
            metadata.distribution("wassden")
            # If we can import the dev packages and wassden is installed,
            # we consider dev mode available
            return True
        except metadata.PackageNotFoundError:
            # If wassden is not found in metadata, assume development installation
            return True

    except Exception:
        return False
