"""Configuration Manager - Core module for managing Claude Code configurations."""

import os
import shutil
from typing import Any
from pathlib import Path

from mycc.modules.mcp import MCPModule
from mycc.modules.configs import ConfigsModule
from mycc.modules.commands import CommandsModule
from mycc.utils.dependencies import DependencyChecker


class ConfigManager:
    """Main configuration manager for MYCC."""

    def __init__(self, project_root: Path, test_mode: bool = False, test_dir: Path | None = None):
        self.project_root = Path(project_root)
        self.test_mode = test_mode or bool(os.getenv("MYCC_TEST_MODE"))

        if self.test_mode:
            # Use test directories
            base_test_dir = test_dir or Path.cwd()
            self.claude_dir = base_test_dir / ".test_claude"
            self.home_dir = base_test_dir / ".test_home"
        else:
            # Production mode
            self.claude_dir = Path.home() / ".claude"
            self.home_dir = Path.home()

        self.config_dir = self.project_root / "config"

        # Initialize dependency checker
        self.dependency_checker = DependencyChecker(self.test_mode)

        # Initialize modules with test mode support
        self.modules = {
            "commands": CommandsModule(self.project_root, self.claude_dir, self.test_mode),
            "configs": ConfigsModule(self.project_root, self.claude_dir, self.test_mode, self.home_dir),
            "mcp": MCPModule(self.project_root, self.claude_dir, self.test_mode),
        }

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.claude_dir.mkdir(parents=True, exist_ok=True)
        (self.claude_dir / "commands").mkdir(parents=True, exist_ok=True)

        # Create ccstatusline config directory
        if self.test_mode:
            ccstatusline_dir = self.home_dir / ".config" / "ccstatusline"
        else:
            ccstatusline_dir = Path.home() / ".config" / "ccstatusline"
        ccstatusline_dir.mkdir(parents=True, exist_ok=True)

        # Create tweakcc config directory
        if self.test_mode:
            tweakcc_dir = self.home_dir / ".tweakcc"
        else:
            tweakcc_dir = Path.home() / ".tweakcc"
        tweakcc_dir.mkdir(parents=True, exist_ok=True)

    def install_module(self, module_name: str) -> bool:
        """Install a specific module."""
        if module_name not in self.modules:
            raise ValueError(f"Unknown module: {module_name}")

        try:
            return self.modules[module_name].install()
        except Exception as e:
            print(f"Error installing {module_name}: {e}")
            return False

    def uninstall_module(self, module_name: str) -> bool:
        """Uninstall a specific module."""
        if module_name not in self.modules:
            raise ValueError(f"Unknown module: {module_name}")

        try:
            return self.modules[module_name].uninstall()
        except Exception as e:
            print(f"Error uninstalling {module_name}: {e}")
            return False

    def link_configs(self) -> bool:
        """Link all configuration files."""
        try:
            # Link Claude settings
            claude_config = self.config_dir / "claude" / "settings.json"
            claude_target = self.claude_dir / "settings.json"

            if claude_config.exists():
                self._create_symlink(claude_config, claude_target)

            # Link ccstatusline settings
            statusline_config = self.config_dir / "ccstatusline" / "settings.json"
            statusline_target = Path.home() / ".config" / "ccstatusline" / "settings.json"

            if statusline_config.exists():
                self._create_symlink(statusline_config, statusline_target)

            return True
        except Exception as e:
            print(f"Error linking configs: {e}")
            return False

    def _create_symlink(self, source: Path, target: Path):
        """Create a symbolic link, backing up existing files."""
        if target.exists() or target.is_symlink():
            # Create backup
            backup_path = target.with_suffix(target.suffix + ".backup")
            if target.exists() and not target.is_symlink():
                shutil.move(str(target), str(backup_path))
            else:
                target.unlink()

        # Create symbolic link
        target.symlink_to(source.resolve())

    def get_status(self) -> dict[str, Any]:
        """Get installation status of all modules."""
        status = {}

        for module_name, module in self.modules.items():
            status[module_name] = {
                "installed": module.is_installed(),
                "description": module.get_description(),
            }

            if status[module_name]["installed"]:
                status[module_name]["path"] = str(module.get_install_path())

        return status

    def get_available_modules(self) -> dict[str, Any]:
        """Get information about available modules."""
        modules_info = {}

        for module_name, module in self.modules.items():
            modules_info[module_name] = {
                "description": module.get_description(),
                "files": module.get_files() if hasattr(module, "get_files") else [],
            }

        return modules_info

    def ensure_dependencies(self, auto_install: bool = True) -> bool:
        """Ensure all dependencies are installed."""
        return self.dependency_checker.check_and_install_all(auto_install)

    def check_dependencies(self) -> dict[str, bool]:
        """Check dependency status without installing."""
        return self.dependency_checker.check_all_dependencies()
