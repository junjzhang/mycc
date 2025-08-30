"""Shared pytest fixtures for MYCC tests."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_test_dirs():
    """Create temporary directories for testing and clean up after."""
    # Create temporary directories
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    claude_dir = temp_path / ".test_claude"
    home_dir = temp_path / ".test_home"
    data_dir = temp_path / ".test_data"

    # Create the directories
    claude_dir.mkdir(parents=True)
    home_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    yield {"temp_path": temp_path, "claude_dir": claude_dir, "home_dir": home_dir, "data_dir": data_dir}

    # Cleanup happens automatically with TemporaryDirectory context manager
    temp_dir.cleanup()


@pytest.fixture
def test_mode_env():
    """Set up test mode environment variable and clean up after."""
    # Set test mode environment variable
    original_value = os.environ.get("MYCC_TEST_MODE")
    os.environ["MYCC_TEST_MODE"] = "1"

    yield

    # Restore original environment
    if original_value is None:
        os.environ.pop("MYCC_TEST_MODE", None)
    else:
        os.environ["MYCC_TEST_MODE"] = original_value


@pytest.fixture
def clean_test_directories():
    """Clean up any test directories that might be left over."""
    # Paths that might be created during testing
    test_paths = [Path.cwd() / ".test_claude", Path.cwd() / ".test_home", Path.cwd() / ".test_data"]

    # Clean up before test
    for path in test_paths:
        if path.exists():
            import shutil

            shutil.rmtree(path, ignore_errors=True)

    yield

    # Clean up after test
    for path in test_paths:
        if path.exists():
            import shutil

            shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def mock_data_files():
    """Create mock data files for testing."""
    from mycc.config import CONFIG_MAPPINGS

    def setup_mock_data(data_dir: Path):
        """Set up mock data files in the given data directory."""
        # Create command files
        commands_dir = data_dir / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        # Create some test command files
        for i in range(5):
            cmd_file = commands_dir / f"test_command_{i}.md"
            cmd_file.write_text(f"# Test Command {i}\n\nThis is test command {i}")

        # Create config files
        config_dir = data_dir / "config"
        for config_key, config_info in CONFIG_MAPPINGS.items():
            config_file = config_dir / config_info["source"]
            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text(f'{{"test": "config for {config_key}"}}')

    return setup_mock_data
