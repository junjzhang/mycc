"""Dependency Module - Simple dependency checking for MYCC.

This module provides basic dependency checking without complex installation logic.
Users are responsible for installing missing dependencies themselves.
"""

import shutil
from typing import Any, Dict
from pathlib import Path

from mycc.external_commands import external_cmd


class DepsModule:
    """Simple dependency checker for MYCC."""

    # Required dependencies with check commands
    DEPENDENCIES = {
        "claude_cli": {
            "name": "Claude Code CLI",
            "check_command": ["claude", "--version"],
            "install_hint": "npm install -g @anthropic-ai/claude-code",
            "required": True,
        },
        "nodejs": {
            "name": "Node.js",
            "check_command": ["node", "--version"],
            "install_hint": "Install from https://nodejs.org",
            "required": True,  # Required for MCP servers
        },
        "npm": {
            "name": "npm",
            "check_command": ["npm", "--version"],
            "install_hint": "Usually comes with Node.js",
            "required": True,
        },
    }

    def __init__(self):
        pass

    def install(self) -> bool:
        """Check all dependencies and report status.

        Note: This doesn't actually install anything, just checks and reports.
        Returns True if all required dependencies are available.
        """
        print("🔍 Checking dependencies...")

        all_ok = True
        for dep_key, dep_info in self.DEPENDENCIES.items():
            status = self._check_dependency(dep_key)
            if status["installed"]:
                print(f"✅ {dep_info['name']} found ({status['version']})")
            else:
                if dep_info["required"]:
                    print(f"❌ {dep_info['name']} not found (required)")
                    print(f"   Install with: {dep_info['install_hint']}")
                    all_ok = False
                else:
                    print(f"⚠️  {dep_info['name']} not found (optional)")

        if all_ok:
            print("✅ All dependencies are ready!")
        else:
            print("❌ Some required dependencies are missing.")
            print("   Please install them manually and run this command again.")

        return all_ok

    def uninstall(self) -> bool:
        """Dependencies are managed externally, nothing to uninstall."""
        print("Dependencies are managed externally. Nothing to uninstall.")
        return True

    def is_installed(self) -> bool:
        """Check if all required dependencies are installed."""
        for dep_key, dep_info in self.DEPENDENCIES.items():
            if dep_info["required"]:
                if not self._check_dependency(dep_key)["installed"]:
                    return False
        return True

    def get_description(self) -> str:
        """Get module description."""
        return "External dependencies (Claude CLI, Node.js, etc.)"

    def get_install_path(self) -> Path:
        """Dependencies don't have a specific install path."""
        return Path("system-managed")

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of all dependencies."""
        status = {}
        for dep_key, dep_info in self.DEPENDENCIES.items():
            dep_status = self._check_dependency(dep_key)
            status[dep_key] = {
                "name": dep_info["name"],
                "installed": dep_status["installed"],
                "version": dep_status["version"],
                "required": dep_info["required"],
                "install_hint": dep_info["install_hint"],
            }
        return status

    def _check_dependency(self, dep_key: str) -> dict:
        """Check if a specific dependency is installed.

        Args:
            dep_key: Key of dependency in DEPENDENCIES dict

        Returns:
            Dict with 'installed' (bool) and 'version' (str or None) keys
        """
        dep_info = self.DEPENDENCIES.get(dep_key)
        if not dep_info:
            return {"installed": False, "version": None}

        # Use unified external command executor
        result = external_cmd.run(dep_info["check_command"], timeout=10)

        if result.success:
            # Extract version from output
            version = result.stdout.strip()
            # Clean up version output (remove extra text)
            if version.startswith("v"):
                version = version[1:]  # Remove 'v' prefix
            version = version.split("\n")[0]  # Take first line only

            return {"installed": True, "version": version}
        else:
            return {"installed": False, "version": None}

    def _check_command_exists(self, command: str) -> bool:
        """Simple check if a command exists in PATH."""
        return shutil.which(command) is not None
