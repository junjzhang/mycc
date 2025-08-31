"""Base class for Claude user setting sub-modules."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pathlib import Path

from mycc.path_manager import PathManager


class BaseSubModule(ABC):
    """Abstract base class for all Claude user setting sub-modules.

    This class defines the common interface and provides shared functionality
    to eliminate code duplication across commands, configs, and mcp modules.
    """

    def __init__(self, claude_dir: Path, home_dir: Path, data_dir: Path):
        """Initialize sub-module with unified path management.

        Args:
            claude_dir: Claude directory path (usually ~/.claude)
            home_dir: User home directory path
            data_dir: Package data directory path
        """
        # Use centralized path manager instead of storing paths directly
        self.paths = PathManager(claude_dir, home_dir, data_dir)

        # Keep original attributes for backward compatibility
        self.claude_dir = claude_dir
        self.home_dir = home_dir
        self.data_dir = data_dir

    @abstractmethod
    def install(self) -> bool:
        """Install this sub-module.

        Returns:
            True if installation was successful
        """
        pass

    @abstractmethod
    def uninstall(self) -> bool:
        """Uninstall this sub-module.

        Returns:
            True if uninstallation was successful
        """
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if this sub-module is installed.

        Returns:
            True if installed
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information.

        Returns:
            Dictionary containing status details
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description.

        Returns:
            Description string
        """
        pass

    @abstractmethod
    def get_install_path(self) -> Path:
        """Get the installation path for this sub-module.

        Returns:
            Path object representing the installation path
        """
        pass
