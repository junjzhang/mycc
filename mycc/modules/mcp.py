"""MCP Module - Manages Model Context Protocol servers."""

import subprocess
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from mycc.core.logger import get_logger
from mycc.modules.base import BaseModule
from mycc.core.resources import ResourceAccessError, read_mcp_servers_json


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""

    name: str
    package: str
    description: str
    scope: str = "user"
    features: list[str] | None = None


class MCPModule(BaseModule):
    """Module for managing MCP servers."""

    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False):
        super().__init__(project_root, target_root, test_mode)
        self.servers: dict[str, MCPServerInfo] = self._load_servers()
        self.logger = get_logger()

    def _load_servers(self) -> dict[str, MCPServerInfo]:
        """Load MCP servers from packaged JSON, with sensible defaults."""
        try:
            # Use unified resource access to read MCP servers configuration
            data = read_mcp_servers_json()
            return self._parse_servers_json(data)
        except ResourceAccessError:
            # Fallback to built-in defaults if resource access fails
            return self._get_builtin_servers()

    def _get_builtin_servers(self) -> dict[str, MCPServerInfo]:
        """Get built-in MCP server definitions as fallback."""
        return {
            "context7": MCPServerInfo(
                name="context7",
                package="npx -y @upstash/context7-mcp",
                description="Context7 MCP server for enhanced context management",
            ),
            "playwright": MCPServerInfo(
                name="playwright",
                package="npx -y @playwright/mcp@latest",
                description="Playwright MCP server for browser automation",
            ),
        }

    def _parse_servers_json(self, data: dict[str, Any]) -> dict[str, MCPServerInfo]:
        servers: dict[str, MCPServerInfo] = {}
        for key, obj in data.items():
            # Allow either key-as-name or explicit name field
            name = obj.get("name", key)
            servers[key] = MCPServerInfo(
                name=name,
                package=obj["package"],
                description=obj.get("description", name),
                scope=obj.get("scope", "user"),
                features=obj.get("features"),
            )
        return servers

    def install(self) -> bool:
        """Install MCP servers."""
        try:
            success = True
            installed_count = 0

            for server_name, server_info in self.servers.items():
                if self._install_mcp_server(server_name, server_info):
                    installed_count += 1
                else:
                    success = False

            if installed_count > 0:
                self.logger.success(f"Installed {installed_count} MCP servers")

            return success

        except Exception as e:
            self.logger.error(f"Error installing MCP servers: {e}")
            return False

    def _install_mcp_server(self, server_name: str, server_info: MCPServerInfo) -> bool:
        """Install a single MCP server."""
        try:
            if self.test_mode:
                self.logger.info(f"[TEST MODE] Simulating MCP server installation: {server_name}")
                return True

            # Check if already installed
            if self._is_server_installed(server_name):
                self.logger.info(f"○ {server_name} already installed")
                return True

            self.logger.info(f"📦 Installing MCP server: {server_name}")

            # Execute claude mcp add command
            scope = server_info.scope or "user"
            cmd = ["claude", "mcp", "add", server_name, "--scope", scope, "--", *server_info.package.split()]

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            self.logger.success(f"Successfully installed {server_name}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.failure(f"Failed to install {server_name}")
            if e.stderr:
                self.logger.warning(f"Error: {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            self.logger.failure(f"Claude Code not found. Please install Claude Code first.")
            return False
        except Exception as e:
            self.logger.failure(f"Unexpected error installing {server_name}: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed MCP servers."""
        try:
            success = True
            removed_count = 0

            for server_name in self.servers.keys():
                if self._uninstall_mcp_server(server_name):
                    removed_count += 1
                else:
                    success = False

            if removed_count > 0:
                self.logger.success(f"Removed {removed_count} MCP servers")

            return success

        except Exception as e:
            self.logger.error(f"Error uninstalling MCP servers: {e}")
            return False

    def _uninstall_mcp_server(self, server_name: str) -> bool:
        """Uninstall a single MCP server."""
        try:
            if self.test_mode:
                self.logger.info(f"[TEST MODE] Simulating MCP server removal: {server_name}")
                return True

            # Check if installed
            if not self._is_server_installed(server_name):
                self.logger.info(f"○ {server_name} not installed")
                return True

            self.logger.info(f"🗑️  Removing MCP server: {server_name}")

            # Execute claude mcp remove command
            subprocess.run(
                ["claude", "mcp", "remove", server_name, "--scope", "user"], capture_output=True, text=True, check=True
            )

            self.logger.success(f"Successfully removed {server_name}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.failure(f"Failed to remove {server_name}")
            if e.stderr:
                self.logger.warning(f"Error: {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            self.logger.failure(f"Claude Code not found.")
            return False
        except Exception as e:
            self.logger.failure(f"Unexpected error removing {server_name}: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if MCP servers are installed."""
        if self.test_mode:
            # In test mode, simulate some servers are installed
            return True

        # Check if any MCP servers are installed
        return any(self._is_server_installed(name) for name in self.servers.keys())

    def _is_server_installed(self, server_name: str) -> bool:
        """Check if a specific MCP server is installed."""
        if self.test_mode:
            return True  # Simulate installed in test mode

        try:
            result = subprocess.run(
                ["claude", "mcp", "list", "--scope", "user"], capture_output=True, text=True, check=True
            )

            # Check if server name appears in the list output
            return server_name in result.stdout

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_description(self) -> str:
        """Get module description."""
        return "MCP (Model Context Protocol) servers"

    def get_install_path(self) -> Path:
        """Get the installation path."""
        return Path("~/.claude/mcp").expanduser()

    def get_available_servers(self) -> list[str]:
        """Get list of available MCP servers."""
        return [f"{name} - {info.description}" for name, info in self.servers.items()]

    def get_installed_servers(self) -> list[str]:
        """Get list of currently installed MCP servers."""
        if self.test_mode:
            return list(self.servers.keys())

        installed = []
        for server_name in self.servers.keys():
            if self._is_server_installed(server_name):
                installed.append(server_name)

        return installed

    def get_files(self) -> list[str]:
        """Get list of available MCP servers for display."""
        return [f"{name} - {info.description}" for name, info in self.servers.items()]
