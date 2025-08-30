"""Claude User Setting Module - Manages all Claude-related user settings.

This module combines the functionality of commands, configs, and mcp modules
into a single, cohesive module that can install components separately or together.
"""

import shutil
import subprocess
from typing import List, Optional
from pathlib import Path

from mycc.config import (
    MCP_SERVERS,
    CONFIG_MAPPINGS,
    COMMAND_PATTERNS,
    get_all_config_keys,
    get_config_source_path,
    get_config_target_path,
    get_all_mcp_server_keys,
)


class ClaudeUserSettingModule:
    """Module for managing Claude user settings (commands, configs, mcp)."""

    def __init__(self, claude_dir: Path, home_dir: Path, data_dir: Path):
        self.claude_dir = claude_dir
        self.home_dir = home_dir
        self.data_dir = data_dir

        # Sub-directories
        self.commands_dir = claude_dir / "commands"

    def install(self, sub_modules: Optional[List[str]] = None) -> bool:
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
        for sub_module in sub_modules:
            if sub_module == "commands":
                success &= self._install_commands()
            elif sub_module == "configs":
                success &= self._install_configs()
            elif sub_module == "mcp":
                success &= self._install_mcp()
            else:
                print(f"❌ Unknown sub-module: {sub_module}")
                success = False

        return success

    def uninstall(self, sub_modules: Optional[List[str]] = None) -> bool:
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
        for sub_module in sub_modules:
            if sub_module == "commands":
                success &= self._uninstall_commands()
            elif sub_module == "configs":
                success &= self._uninstall_configs()
            elif sub_module == "mcp":
                success &= self._uninstall_mcp()
            else:
                print(f"❌ Unknown sub-module: {sub_module}")
                success = False

        return success

    def is_installed(self, sub_modules: Optional[List[str]] = None) -> bool:
        """Check if Claude user settings are installed.

        Args:
            sub_modules: List of sub-modules to check. If None, checks all.

        Returns:
            True if all requested sub-modules are installed
        """
        if sub_modules is None:
            sub_modules = ["commands", "configs", "mcp"]

        for sub_module in sub_modules:
            if sub_module == "commands" and not self._is_commands_installed():
                return False
            elif sub_module == "configs" and not self._is_configs_installed():
                return False
            elif sub_module == "mcp" and not self._is_mcp_installed():
                return False

        return True

    def get_description(self) -> str:
        """Get module description."""
        return "Claude user settings (commands, configs, mcp)"

    def get_install_path(self) -> Path:
        """Get the main installation path."""
        return self.claude_dir

    def get_status(self) -> dict:
        """Get detailed status of all sub-modules."""
        return {
            "commands": self._get_commands_status(),
            "configs": self._get_configs_status(),
            "mcp": self._get_mcp_status(),
        }

    # Commands sub-module methods
    def _install_commands(self) -> bool:
        """Install command files to ~/.claude/commands/."""
        try:
            commands_source_dir = self.data_dir / "commands"

            if not commands_source_dir.exists():
                print(f"❌ Commands source directory not found: {commands_source_dir}")
                return False

            # Get all command files
            command_files = []
            for pattern in COMMAND_PATTERNS:
                command_files.extend(commands_source_dir.glob(pattern))

            if not command_files:
                print("❌ No command files found")
                return False

            # Ensure target directory exists
            self.commands_dir.mkdir(parents=True, exist_ok=True)

            # Copy all command files
            copied_count = 0
            for cmd_file in command_files:
                try:
                    target_file = self.commands_dir / cmd_file.name
                    shutil.copy2(cmd_file, target_file)
                    copied_count += 1
                except Exception as e:
                    print(f"❌ Failed to copy {cmd_file.name}: {e}")
                    continue

            if copied_count > 0:
                print(f"✅ Installed {copied_count} commands to {self.commands_dir}")
                return True
            else:
                print("❌ Failed to install any command files")
                return False

        except Exception as e:
            print(f"❌ Error installing commands: {e}")
            return False

    def _uninstall_commands(self) -> bool:
        """Remove installed command files."""
        try:
            if not self.commands_dir.exists():
                print("✅ Commands already uninstalled")
                return True

            removed_count = 0
            for pattern in COMMAND_PATTERNS:
                for cmd_file in self.commands_dir.glob(pattern):
                    try:
                        cmd_file.unlink()
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Failed to remove {cmd_file.name}: {e}")

            print(f"✅ Removed {removed_count} command files")
            return True

        except Exception as e:
            print(f"❌ Error uninstalling commands: {e}")
            return False

    def _is_commands_installed(self) -> bool:
        """Check if commands are installed."""
        if not self.commands_dir.exists():
            return False

        # Check if there are any command files
        for pattern in COMMAND_PATTERNS:
            if list(self.commands_dir.glob(pattern)):
                return True
        return False

    def _get_commands_status(self) -> dict:
        """Get commands sub-module status."""
        installed = self._is_commands_installed()
        file_count = 0

        if installed:
            for pattern in COMMAND_PATTERNS:
                file_count += len(list(self.commands_dir.glob(pattern)))

        return {
            "installed": installed,
            "file_count": file_count,
            "path": str(self.commands_dir),
            "description": f"{file_count} command files" if installed else "not installed",
        }

    # Configs sub-module methods
    def _install_configs(self) -> bool:
        """Install configuration files by creating symbolic links."""
        try:
            success = True
            installed_count = 0

            for config_key in get_all_config_keys():
                try:
                    if self._install_single_config(config_key):
                        installed_count += 1
                    else:
                        success = False
                except Exception as e:
                    print(f"❌ Error installing {config_key}: {e}")
                    success = False

            if installed_count > 0:
                print(f"✅ Installed {installed_count} configuration links")

            return success

        except Exception as e:
            print(f"❌ Error installing configs: {e}")
            return False

    def _install_single_config(self, config_key: str) -> bool:
        """Install a single configuration file."""
        config_info = CONFIG_MAPPINGS[config_key]

        # Get source and target paths
        source_path = get_config_source_path(config_key, self.data_dir)
        target_path = get_config_target_path(config_key, self.home_dir)

        # Check if source exists
        if not source_path.exists():
            print(f"⚠️ Config source not found: {source_path}")
            return False

        # Create target directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle existing target
        if target_path.exists() or target_path.is_symlink():
            if config_info.get("backup_existing", True) and target_path.exists() and not target_path.is_symlink():
                # Create backup of regular file
                backup_path = target_path.with_suffix(target_path.suffix + ".backup")
                target_path.rename(backup_path)
                print(f"📋 Backed up existing {config_info['name']} to {backup_path}")
            else:
                # Remove existing file/symlink
                target_path.unlink()

        # Create symbolic link
        target_path.symlink_to(source_path.resolve())
        print(f"✅ Linked {config_info['name']}")
        return True

    def _uninstall_configs(self) -> bool:
        """Remove installed configuration file links."""
        try:
            success = True
            removed_count = 0

            for config_key in get_all_config_keys():
                try:
                    target_path = get_config_target_path(config_key, self.home_dir)
                    if target_path.is_symlink():
                        target_path.unlink()
                        removed_count += 1
                        config_info = CONFIG_MAPPINGS[config_key]
                        print(f"✅ Removed {config_info['name']} link")
                except Exception as e:
                    print(f"❌ Error removing {config_key}: {e}")
                    success = False

            print(f"✅ Removed {removed_count} configuration links")
            return success

        except Exception as e:
            print(f"❌ Error uninstalling configs: {e}")
            return False

    def _is_configs_installed(self) -> bool:
        """Check if configs are installed."""
        for config_key in get_all_config_keys():
            target_path = get_config_target_path(config_key, self.home_dir)
            if target_path.is_symlink():
                return True
        return False

    def _get_configs_status(self) -> dict:
        """Get configs sub-module status."""
        linked_configs = []
        missing_configs = []

        for config_key in get_all_config_keys():
            target_path = get_config_target_path(config_key, self.home_dir)
            config_info = CONFIG_MAPPINGS[config_key]

            if target_path.is_symlink():
                linked_configs.append(config_info["name"])
            else:
                missing_configs.append(str(target_path))

        installed = len(linked_configs) > 0

        return {
            "installed": installed,
            "linked_count": len(linked_configs),
            "missing_count": len(missing_configs),
            "linked_configs": linked_configs,
            "missing_configs": missing_configs,
            "description": f"{len(linked_configs)} configs linked" if installed else "not installed",
        }

    # MCP sub-module methods
    def _install_mcp(self) -> bool:
        """Install MCP servers."""
        try:
            success = True
            installed_count = 0

            for server_key in get_all_mcp_server_keys():
                try:
                    if self._install_single_mcp_server(server_key):
                        installed_count += 1
                    else:
                        success = False
                except Exception as e:
                    print(f"❌ Error installing MCP server {server_key}: {e}")
                    success = False

            if installed_count > 0:
                print(f"✅ Installed {installed_count} MCP servers")

            return success

        except Exception as e:
            print(f"❌ Error installing MCP servers: {e}")
            return False

    def _install_single_mcp_server(self, server_key: str) -> bool:
        """Install a single MCP server."""
        server_info = MCP_SERVERS[server_key]

        # Check if already installed
        if self._is_mcp_server_installed(server_key):
            print(f"⚪ {server_info['name']} already installed")
            return True

        print(f"📦 Installing MCP server: {server_info['name']}")

        try:
            # Execute claude mcp add command
            scope = server_info.get("scope", "user")
            cmd = ["claude", "mcp", "add", server_key, "-s", scope, "--"] + server_info["package"].split()

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print(f"✅ Successfully installed {server_info['name']}")
                return True
            else:
                print(f"❌ Failed to install {server_info['name']}")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout installing {server_info['name']}")
            return False
        except FileNotFoundError:
            print("❌ Claude Code CLI not found. Please install it first.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error installing {server_info['name']}: {e}")
            return False

    def _uninstall_mcp(self) -> bool:
        """Uninstall MCP servers."""
        try:
            success = True
            removed_count = 0

            for server_key in get_all_mcp_server_keys():
                try:
                    if self._uninstall_single_mcp_server(server_key):
                        removed_count += 1
                    else:
                        success = False
                except Exception as e:
                    print(f"❌ Error uninstalling MCP server {server_key}: {e}")
                    success = False

            if removed_count > 0:
                print(f"✅ Removed {removed_count} MCP servers")

            return success

        except Exception as e:
            print(f"❌ Error uninstalling MCP servers: {e}")
            return False

    def _uninstall_single_mcp_server(self, server_key: str) -> bool:
        """Uninstall a single MCP server."""
        server_info = MCP_SERVERS[server_key]

        # Check if installed
        if not self._is_mcp_server_installed(server_key):
            print(f"⚪ {server_info['name']} not installed")
            return True

        print(f"🗑️ Removing MCP server: {server_info['name']}")

        try:
            # Execute claude mcp remove command
            cmd = ["claude", "mcp", "remove", server_key, "-s", "user"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print(f"✅ Successfully removed {server_info['name']}")
                return True
            else:
                print(f"❌ Failed to remove {server_info['name']}")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout removing {server_info['name']}")
            return False
        except FileNotFoundError:
            print("❌ Claude Code CLI not found.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error removing {server_info['name']}: {e}")
            return False

    def _is_mcp_installed(self) -> bool:
        """Check if any MCP servers are installed."""
        for server_key in get_all_mcp_server_keys():
            if self._is_mcp_server_installed(server_key):
                return True
        return False

    def _is_mcp_server_installed(self, server_key: str) -> bool:
        """Check if a specific MCP server is installed."""
        try:
            result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                # Look for server_key at the beginning of a line followed by ': '
                # This matches the format: "context7: npx -y @upstash/context7-mcp - ✓ Connected"
                import re

                pattern = rf"^{re.escape(server_key)}:\s"
                return bool(re.search(pattern, result.stdout, re.MULTILINE))
            else:
                return False

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def _get_mcp_status(self) -> dict:
        """Get MCP sub-module status."""
        installed_servers = []
        available_servers = list(get_all_mcp_server_keys())

        for server_key in available_servers:
            if self._is_mcp_server_installed(server_key):
                server_info = MCP_SERVERS[server_key]
                installed_servers.append(server_info["name"])

        installed = len(installed_servers) > 0

        return {
            "installed": installed,
            "installed_count": len(installed_servers),
            "available_count": len(available_servers),
            "installed_servers": installed_servers,
            "available_servers": [MCP_SERVERS[k]["name"] for k in available_servers],
            "description": f"{len(installed_servers)} servers installed" if installed else "not installed",
        }
