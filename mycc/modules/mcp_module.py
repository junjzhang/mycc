"""MCP sub-module for managing Model Context Protocol servers."""

import re
from typing import Any, Dict
from pathlib import Path

from mycc.config import MCP_SERVERS, get_all_mcp_server_keys
from mycc.external_commands import external_cmd
from mycc.modules.base_sub_module import BaseSubModule


class McpModule(BaseSubModule):
    """Handles MCP server installation via Claude CLI.

    This module manages the installation and removal of MCP servers
    using the Claude Code CLI's MCP management commands.
    """

    def install(self) -> bool:
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

    def uninstall(self) -> bool:
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

    def is_installed(self) -> bool:
        """Check if any MCP servers are installed."""
        for server_key in get_all_mcp_server_keys():
            if self._is_mcp_server_installed(server_key):
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
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

    def get_description(self) -> str:
        """Get human-readable description."""
        return "Model Context Protocol (MCP) servers"

    def get_install_path(self) -> Path:
        """Get installation path."""
        return self.claude_dir

    def _install_single_mcp_server(self, server_key: str) -> bool:
        """Install a single MCP server."""
        server_info = MCP_SERVERS[server_key]

        # Check if already installed
        if self._is_mcp_server_installed(server_key):
            print(f"⚪ {server_info['name']} already installed")
            return True

        print(f"📦 Installing MCP server: {server_info['name']}")

        # Execute claude mcp add command
        scope = server_info.get("scope", "user")
        cmd = ["claude", "mcp", "add", server_key, "-s", scope, "--"] + server_info["package"].split()

        result = external_cmd.run(cmd, timeout=120)

        if result.success:
            print(f"✅ Successfully installed {server_info['name']}")
            return True
        else:
            print(f"❌ Failed to install {server_info['name']}")
            if result.timed_out:
                print("   Error: Installation timed out after 120 seconds")
            elif result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False

    def _uninstall_single_mcp_server(self, server_key: str) -> bool:
        """Uninstall a single MCP server."""
        server_info = MCP_SERVERS[server_key]

        # Check if installed
        if not self._is_mcp_server_installed(server_key):
            print(f"⚪ {server_info['name']} not installed")
            return True

        print(f"🗑️ Removing MCP server: {server_info['name']}")

        # Execute claude mcp remove command
        scope = server_info.get("scope", "user")
        cmd = ["claude", "mcp", "remove", server_key, "-s", scope]

        result = external_cmd.run(cmd, timeout=60)

        if result.success:
            print(f"✅ Successfully removed {server_info['name']}")
            return True
        else:
            print(f"❌ Failed to remove {server_info['name']}")
            if result.timed_out:
                print("   Error: Removal timed out after 60 seconds")
            elif result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False

    def _is_mcp_server_installed(self, server_key: str) -> bool:
        """Check if a specific MCP server is installed."""
        result = external_cmd.run(["claude", "mcp", "list"], timeout=30)

        if result.success:
            # Look for server_key at the beginning of a line followed by ': '
            # This matches the format: "context7: npx -y @upstash/context7-mcp - ✓ Connected"
            pattern = rf"^{re.escape(server_key)}:\s"
            return bool(re.search(pattern, result.stdout, re.MULTILINE))
        else:
            return False
