"""Test development feature gate functionality."""

from unittest.mock import patch

from typer.testing import CliRunner


class TestDevGate:
    """Test development mode gating functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.utils.dev_gate.is_dev_mode")
    def test_experiment_command_not_available_without_dev_mode(self, mock_is_dev_mode):
        """Test that experiment command is not available when dev mode is disabled."""
        # Mock dev mode as disabled before any imports
        mock_is_dev_mode.return_value = False

        # Clear any previously imported modules to ensure clean state
        import sys  # noqa: PLC0415

        modules_to_remove = ["wassden.cli", "wassden.clis.core", "wassden.clis.experiment"]
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]

        # Now import with mocked dev mode
        from wassden.cli import app  # noqa: PLC0415

        # Test that experiment command is not in help
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "experiment" not in result.stdout

        # Test that experiment command is not available
        result = self.runner.invoke(app, ["experiment", "--help"])
        assert result.exit_code != 0  # Should fail because command doesn't exist

    @patch("wassden.utils.dev_gate.is_dev_mode")
    def test_experiment_command_available_with_dev_mode(self, mock_is_dev_mode):
        """Test that experiment command is available when dev mode is enabled."""
        # Mock dev mode as enabled
        mock_is_dev_mode.return_value = True

        # Clear any previously imported modules to ensure clean state
        import sys  # noqa: PLC0415

        modules_to_remove = ["wassden.cli", "wassden.clis.core", "wassden.clis.experiment"]
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]

        # Now import with mocked dev mode
        from wassden.cli import app  # noqa: PLC0415

        # Test that experiment command is in help
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "experiment" in result.stdout

        # Test that experiment command is available and shows help
        result = self.runner.invoke(app, ["experiment", "--help"])
        assert result.exit_code == 0
        assert "Experiment runner commands" in result.stdout

    def test_dev_mode_detection_with_dev_packages(self):
        """Test dev mode detection when dev packages are available."""
        from wassden.utils.dev_gate import is_dev_mode  # noqa: PLC0415

        # In current environment with dev dependencies, should return True
        assert is_dev_mode() is True

    @patch("wassden.utils.dev_gate.importlib.util.find_spec")
    def test_dev_mode_detection_without_dev_packages(self, mock_find_spec):
        """Test dev mode detection when dev packages are not available."""
        # Mock that dev packages are not found
        mock_find_spec.side_effect = ImportError("Module not found")

        from wassden.utils.dev_gate import is_dev_mode  # noqa: PLC0415

        # Should return False when dev packages are not available
        assert is_dev_mode() is False
