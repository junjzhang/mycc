"""Unified path management for MYCC.

This module centralizes all path operations that were previously scattered across:
- config.py: Config file path resolution functions
- base_sub_module.py: Directory path storage
- Various modules: Path calculations and directory operations

Eliminates path handling duplication and provides a single source of truth.
"""

from typing import Dict, Optional
from pathlib import Path

from mycc.config import CONFIG_MAPPINGS


class PathManager:
    """Centralized path manager for all MYCC operations.

    This class consolidates all path-related logic that was previously scattered
    across multiple files, providing a single, consistent interface for:
    - Claude directory structure
    - Configuration file paths (source and target)
    - Command file locations
    - Data directory organization
    """

    def __init__(
        self, claude_dir: Optional[Path] = None, home_dir: Optional[Path] = None, data_dir: Optional[Path] = None
    ):
        """Initialize path manager with dependency injection.

        Args:
            claude_dir: Claude directory path (defaults to ~/.claude)
            home_dir: User home directory path (defaults to ~)
            data_dir: Package data directory path (defaults to package data)
        """
        # Set default paths if not provided
        self.claude_dir = claude_dir or (Path.home() / ".claude")
        self.home_dir = home_dir or Path.home()
        self.data_dir = data_dir or (Path(__file__).parent / "data")

        # Derived paths - computed once, used everywhere
        self._commands_dir = self.claude_dir / "commands"
        self._config_data_dir = self.data_dir / "config"
        self._commands_data_dir = self.data_dir / "commands"

    @property
    def commands_dir(self) -> Path:
        """Get the commands installation directory (~/.claude/commands)."""
        return self._commands_dir

    @property
    def config_data_dir(self) -> Path:
        """Get the configuration data directory (package/data/config)."""
        return self._config_data_dir

    @property
    def commands_data_dir(self) -> Path:
        """Get the commands data directory (package/data/commands)."""
        return self._commands_data_dir

    def get_config_source_path(self, config_key: str) -> Path:
        """Get the source path for a configuration file.

        Args:
            config_key: Configuration key from CONFIG_MAPPINGS

        Returns:
            Path to the source configuration file

        Raises:
            ValueError: If config_key is unknown
        """
        config_info = CONFIG_MAPPINGS.get(config_key)
        if not config_info:
            raise ValueError(f"Unknown config key: {config_key}")

        return self.config_data_dir / config_info["source"]

    def get_config_target_path(self, config_key: str) -> Path:
        """Get the target path for a configuration file.

        Args:
            config_key: Configuration key from CONFIG_MAPPINGS

        Returns:
            Path where the configuration file should be installed

        Raises:
            ValueError: If config_key is unknown
        """
        config_info = CONFIG_MAPPINGS.get(config_key)
        if not config_info:
            raise ValueError(f"Unknown config key: {config_key}")

        if config_info["relative_to_home"]:
            return self.home_dir / config_info["target"]
        else:
            return Path(config_info["target"])

    def get_all_config_paths(self) -> Dict[str, Dict[str, Path]]:
        """Get all configuration file paths (source and target).

        Returns:
            Dictionary mapping config keys to their source and target paths
        """
        paths = {}
        for config_key in CONFIG_MAPPINGS.keys():
            paths[config_key] = {
                "source": self.get_config_source_path(config_key),
                "target": self.get_config_target_path(config_key),
            }
        return paths

    def ensure_directories(self) -> None:
        """Ensure all required directories exist.

        Creates necessary directories if they don't exist:
        - Claude directory and commands subdirectory
        - Parent directories for all config target paths
        """
        # Ensure Claude directories exist
        self.commands_dir.mkdir(parents=True, exist_ok=True)

        # Ensure config target directories exist
        for config_key in CONFIG_MAPPINGS.keys():
            target_path = self.get_config_target_path(config_key)
            target_path.parent.mkdir(parents=True, exist_ok=True)

    def validate_data_paths(self) -> Dict[str, bool]:
        """Validate that all required data paths exist.

        Returns:
            Dictionary mapping path names to their existence status
        """
        return {
            "data_dir": self.data_dir.exists(),
            "config_data_dir": self.config_data_dir.exists(),
            "commands_data_dir": self.commands_data_dir.exists(),
        }

    def get_path_info(self) -> Dict[str, str]:
        """Get summary information about all managed paths.

        Returns:
            Dictionary with path information for debugging/status display
        """
        return {
            "claude_dir": str(self.claude_dir),
            "home_dir": str(self.home_dir),
            "data_dir": str(self.data_dir),
            "commands_dir": str(self.commands_dir),
            "config_data_dir": str(self.config_data_dir),
            "commands_data_dir": str(self.commands_data_dir),
        }
