"""Simplified Module Manager for MYCC.

This replaces the complex core/manager.py with a simple, direct approach
that manages only two modules: deps and claude_user_setting.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path

from mycc.modules.deps import DepsModule
from mycc.modules.claude_user_setting import ClaudeUserSettingModule


class ModuleManager:
    """Simplified manager for MYCC modules using dependency injection."""

    def __init__(
        self, claude_dir: Optional[Path] = None, home_dir: Optional[Path] = None, data_dir: Optional[Path] = None
    ):
        """Initialize module manager with dependency injection.

        Args:
            claude_dir: Claude directory path (defaults to ~/.claude)
            home_dir: Home directory path (defaults to ~)
            data_dir: Data directory path (defaults to package data)
        """
        # Set default paths if not provided
        self.claude_dir = claude_dir or (Path.home() / ".claude")
        self.home_dir = home_dir or Path.home()

        # Data directory - try to find package data
        if data_dir:
            self.data_dir = data_dir
        else:
            # Try to find data directory relative to this file
            package_root = Path(__file__).parent
            self.data_dir = package_root / "data"

            # If that doesn't exist, try importlib.resources approach
            if not self.data_dir.exists():
                try:
                    from importlib import resources

                    import mycc.data

                    self.data_dir = Path(str(resources.files(mycc.data)))
                except (ImportError, AttributeError):
                    # Fallback to package root
                    self.data_dir = package_root / "data"

        # Initialize modules
        self.deps = DepsModule()
        self.claude_user_setting = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        # Module registry for easy access
        self.modules = {"deps": self.deps, "claude_user_setting": self.claude_user_setting}

    def install_module(self, module_name: str, **kwargs) -> bool:
        """Install a specific module.

        Args:
            module_name: Name of module to install ('deps' or 'claude_user_setting')
            **kwargs: Additional arguments for the module (e.g., sub_modules for claude_user_setting)

        Returns:
            True if installation was successful
        """
        if module_name not in self.modules:
            print(f"❌ Unknown module: {module_name}")
            return False

        try:
            module = self.modules[module_name]

            # Special handling for claude_user_setting sub-modules
            if module_name == "claude_user_setting" and "sub_modules" in kwargs:
                return module.install(kwargs["sub_modules"])
            else:
                return module.install()

        except Exception as e:
            print(f"❌ Error installing {module_name}: {e}")
            return False

    def uninstall_module(self, module_name: str, **kwargs) -> bool:
        """Uninstall a specific module.

        Args:
            module_name: Name of module to uninstall
            **kwargs: Additional arguments for the module

        Returns:
            True if uninstallation was successful
        """
        if module_name not in self.modules:
            print(f"❌ Unknown module: {module_name}")
            return False

        try:
            module = self.modules[module_name]

            # Special handling for claude_user_setting sub-modules
            if module_name == "claude_user_setting" and "sub_modules" in kwargs:
                return module.uninstall(kwargs["sub_modules"])
            else:
                return module.uninstall()

        except Exception as e:
            print(f"❌ Error uninstalling {module_name}: {e}")
            return False

    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific module.

        Args:
            module_name: Name of module to check

        Returns:
            Dictionary containing module status information
        """
        if module_name not in self.modules:
            return {"error": f"Unknown module: {module_name}"}

        try:
            module = self.modules[module_name]

            status = {
                "name": module_name,
                "description": module.get_description(),
                "installed": module.is_installed(),
                "install_path": str(module.get_install_path()),
            }

            # Get detailed status if available
            if hasattr(module, "get_status"):
                status["details"] = module.get_status()

            return status

        except Exception as e:
            return {"error": f"Error checking {module_name}: {e}"}

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all modules.

        Returns:
            Dictionary containing status of all modules
        """
        status = {}
        for module_name in self.modules:
            status[module_name] = self.get_module_status(module_name)
        return status

    def install_multiple_modules(self, module_specs: List[str]) -> bool:
        """Install multiple modules.

        Args:
            module_specs: List of module specifications (e.g., ['deps', 'claude_user_setting'])

        Returns:
            True if all installations were successful
        """
        success = True
        for spec in module_specs:
            if not self.install_module(spec):
                success = False
        return success

    def install_all(self) -> bool:
        """Install all available modules.

        Returns:
            True if all installations were successful
        """
        print("📦 Installing all modules...")
        return self.install_multiple_modules(["deps", "claude_user_setting"])

    def get_available_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available modules.

        Returns:
            Dictionary containing information about each module
        """
        modules_info = {}

        for module_name, module in self.modules.items():
            try:
                info = {
                    "name": module_name,
                    "description": module.get_description(),
                    "install_path": str(module.get_install_path()),
                }

                # Add sub-module information for claude_user_setting
                if module_name == "claude_user_setting":
                    info["sub_modules"] = ["commands", "configs", "mcp"]
                    info["sub_module_descriptions"] = {
                        "commands": "Claude slash commands (25 .md files)",
                        "configs": "Configuration file links (3 configs)",
                        "mcp": "MCP server installations (1 server)",
                    }

                modules_info[module_name] = info

            except Exception as e:
                modules_info[module_name] = {"error": str(e)}

        return modules_info

    def list_modules(self) -> None:
        """Print a list of available modules."""
        print("Available Modules:")
        print("=" * 40)

        modules_info = self.get_available_modules()

        for module_name, info in modules_info.items():
            if "error" in info:
                print(f"❌ {module_name:<20} Error: {info['error']}")
            else:
                print(f"📦 {module_name:<20} {info['description']}")

                # Show sub-modules if available
                if "sub_modules" in info:
                    for sub_module in info["sub_modules"]:
                        sub_desc = info["sub_module_descriptions"].get(sub_module, "")
                        print(f"   ├── {sub_module:<16} {sub_desc}")

    def show_status(self, module_name: Optional[str] = None) -> None:
        """Print detailed status information.

        Args:
            module_name: Specific module to show status for. If None, shows all modules.
        """
        if module_name:
            self._show_single_module_status(module_name)
        else:
            self._show_all_modules_status()

    def _show_single_module_status(self, module_name: str) -> None:
        """Show status for a single module."""
        status = self.get_module_status(module_name)

        if "error" in status:
            print(f"❌ Error: {status['error']}")
            return

        # Print header
        module_display = module_name.replace("_", " ").title()
        print(f"{module_display} Status")
        print("=" * 40)

        # Show basic info
        installed_icon = "✅" if status["installed"] else "❌"
        print(f"{installed_icon} {status['name']:<20} {status['description']}")

        if status["installed"]:
            print(f"   Path: {status['install_path']}")

        # Show detailed info if available
        if "details" in status:
            self._show_detailed_status(status["details"])

    def _show_all_modules_status(self) -> None:
        """Show status for all modules."""
        print("MYCC Status")
        print("=" * 40)

        all_status = self.get_all_status()
        all_modules_ok = True

        for module_name, status in all_status.items():
            if "error" in status:
                print(f"❌ {module_name:<20} Error: {status['error']}")
                all_modules_ok = False
                continue

            # Show main module status
            installed_icon = "✅" if status["installed"] else "❌"
            if not status["installed"]:
                all_modules_ok = False

            print(f"{installed_icon} {module_name:<20} {status['description']}")

            if status["installed"]:
                print(f"   Path: {status['install_path']}")

            # Show detailed sub-module status
            if "details" in status:
                self._show_detailed_status(status["details"], indent="   ")

            print()  # Empty line between modules

        # Overall status
        if all_modules_ok:
            print("Installation Status: All modules ready ✨")
        else:
            print("Installation Status: Some modules need attention ⚠️")

    def _show_detailed_status(self, details: Dict[str, Any], indent: str = "") -> None:
        """Show detailed status information."""
        for sub_name, sub_info in details.items():
            if isinstance(sub_info, dict) and "installed" in sub_info:
                icon = "✅" if sub_info["installed"] else "❌"
                desc = sub_info.get("description", "no info")
                print(f"{indent}├── {sub_name:<12} {icon} {desc}")

                # Show additional details
                if sub_info["installed"]:
                    if "path" in sub_info:
                        print(f"{indent}│   Path: {sub_info['path']}")
                    if "linked_configs" in sub_info:
                        for config in sub_info["linked_configs"]:
                            print(f"{indent}│   ✓ {config}")
                    if "installed_servers" in sub_info:
                        for server in sub_info["installed_servers"]:
                            print(f"{indent}│   ✓ {server}")
                else:
                    # Show what's missing
                    if "missing_configs" in sub_info:
                        print(f"{indent}│   Missing links:")
                        for config in sub_info["missing_configs"][:3]:  # Show first 3
                            print(f"{indent}│   - {config}")
                    if "available_servers" in sub_info:
                        print(f"{indent}│   Available: {', '.join(sub_info['available_servers'])}")

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.claude_dir.mkdir(parents=True, exist_ok=True)
        (self.claude_dir / "commands").mkdir(parents=True, exist_ok=True)
