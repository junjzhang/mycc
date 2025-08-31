"""Protocol interfaces for MYCC modules.

This module defines the standard interfaces that all MYCC modules must implement,
ensuring consistency and type safety across the codebase.
"""

from typing import Any, Dict, Protocol
from pathlib import Path


class ModuleInterface(Protocol):
    """Standard interface that all MYCC modules must implement.

    This Protocol ensures consistency across all modules:
    - deps.py: System dependency management
    - claude_user_setting.py: User configuration management
    - All sub-modules: commands, configs, mcp
    """

    def install(self, **kwargs) -> bool:
        """Install the module.

        Args:
            **kwargs: Module-specific arguments (e.g., sub_modules for claude_user_setting)

        Returns:
            True if installation was successful
        """
        ...

    def uninstall(self, **kwargs) -> bool:
        """Uninstall the module.

        Args:
            **kwargs: Module-specific arguments

        Returns:
            True if uninstallation was successful
        """
        ...

    def is_installed(self, **kwargs) -> bool:
        """Check if the module is installed.

        Args:
            **kwargs: Module-specific arguments

        Returns:
            True if module is installed
        """
        ...

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information for the module.

        Returns:
            Dictionary containing module status information
        """
        ...

    def get_description(self) -> str:
        """Get human-readable description of the module.

        Returns:
            Brief description string
        """
        ...

    def get_install_path(self) -> Path:
        """Get the installation path for the module.

        Returns:
            Path object representing the installation path
        """
        ...
