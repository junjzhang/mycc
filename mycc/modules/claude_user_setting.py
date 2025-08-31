"""Claude User Setting Module - Orchestrates Claude-related user settings.

This module acts as a coordinator for commands, configs, and mcp sub-modules,
providing a unified interface while delegating actual work to specialized modules.
"""

from typing import Any
from pathlib import Path

from mycc.modules.mcp_module import McpModule
from mycc.modules.configs_module import ConfigsModule
from mycc.modules.commands_module import CommandsModule


class ClaudeUserSettingModule:
    """Orchestrator for Claude user settings sub-modules.

    This class provides a unified interface for managing commands, configs,
    and MCP servers while delegating actual implementation to specialized modules.
    """

    def __init__(self, claude_dir: Path, home_dir: Path, data_dir: Path):
        """Initialize the orchestrator with sub-modules.

        Args:
            claude_dir: Claude directory path (usually ~/.claude)
            home_dir: User home directory path
            data_dir: Package data directory path
        """
        # Initialize sub-modules
        self.commands = CommandsModule(claude_dir, home_dir, data_dir)
        self.configs = ConfigsModule(claude_dir, home_dir, data_dir)
        self.mcp = McpModule(claude_dir, home_dir, data_dir)

        # Sub-module registry for easy access
        self._sub_modules = {"commands": self.commands, "configs": self.configs, "mcp": self.mcp}

        # Keep paths for compatibility
        self.claude_dir = claude_dir
        self.home_dir = home_dir
        self.data_dir = data_dir

    def install(self, sub_modules: list[str] | None = None) -> bool:
        """Install Claude user settings.

        Args:
            sub_modules: List of sub-modules to install. If None, installs all.
                        Valid values: ['commands', 'configs', 'mcp']

        Returns:
            True if all requested sub-modules were installed successfully
        """
        if sub_modules is None:
            sub_modules = ["commands", "configs", "mcp"]

        print(f"📦 Installing Claude user settings: {', '.join(sub_modules)}")

        success = True
        for sub_module_name in sub_modules:
            module = self._sub_modules.get(sub_module_name)
            if module:
                success &= module.install()
            else:
                print(f"❌ Unknown sub-module: {sub_module_name}")
                success = False

        return success

    def uninstall(self, sub_modules: list[str] | None = None) -> bool:
        """Uninstall Claude user settings.

        Args:
            sub_modules: List of sub-modules to uninstall. If None, uninstalls all.

        Returns:
            True if all requested sub-modules were uninstalled successfully
        """
        if sub_modules is None:
            sub_modules = ["commands", "configs", "mcp"]

        print(f"🗑️ Uninstalling Claude user settings: {', '.join(sub_modules)}")

        success = True
        for sub_module_name in sub_modules:
            module = self._sub_modules.get(sub_module_name)
            if module:
                success &= module.uninstall()
            else:
                print(f"❌ Unknown sub-module: {sub_module_name}")
                success = False

        return success

    def is_installed(self, sub_modules: list[str] | None = None) -> bool:
        """Check if Claude user settings are installed.

        Args:
            sub_modules: List of sub-modules to check. If None, checks all.

        Returns:
            True if all requested sub-modules are installed
        """
        if sub_modules is None:
            sub_modules = ["commands", "configs", "mcp"]

        for sub_module_name in sub_modules:
            module = self._sub_modules.get(sub_module_name)
            if module and not module.is_installed():
                return False

        return True

    def get_description(self) -> str:
        """Get module description."""
        return "Claude user settings (commands, configs, mcp)"

    def get_install_path(self) -> Path:
        """Get the main installation path."""
        return self.claude_dir

    def get_status(self) -> dict[str, Any]:
        """Get detailed status of all sub-modules."""
        return {name: module.get_status() for name, module in self._sub_modules.items()}
