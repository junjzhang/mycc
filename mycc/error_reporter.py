"""Unified error reporting system for MYCC.

This module provides consistent, user-friendly error messages with actionable suggestions,
eliminating the scattered "❌ " error messages throughout the codebase.
"""

from typing import Optional


class ErrorReporter:
    """Centralized error reporting with user-friendly messages and suggestions.

    This class provides consistent error formatting and actionable advice
    to help users resolve issues quickly.
    """

    @staticmethod
    def module_not_found(module_name: str) -> str:
        """Report unknown module error."""
        return (
            f"❌ Unknown module: {module_name}\n"
            f"💡 Available modules: deps, claude_user_setting\n"
            f"   Sub-modules: commands, configs, mcp"
        )

    @staticmethod
    def subprocess_failed(command: str, error_message: str) -> str:
        """Report subprocess execution failure with installation hints.

        Args:
            command: The command that failed
            error_message: Error details

        Returns:
            Formatted error message with installation suggestion
        """
        cmd_name = command.split()[0] if command else ""

        # Command-specific installation hints
        installation_hints = {
            "claude": "Install Claude CLI: npm install -g @anthropic-ai/claude-code",
            "node": "Install Node.js: https://nodejs.org/download/",
            "npm": "Install npm (usually comes with Node.js): https://nodejs.org/",
            "git": "Install Git: https://git-scm.com/downloads",
        }

        base_message = f"❌ Command failed: {command}\n{error_message}"

        hint = installation_hints.get(cmd_name)
        if hint:
            return f"{base_message}\n💡 {hint}"
        else:
            return f"{base_message}\n💡 Make sure '{cmd_name}' is installed and in your PATH"

    @staticmethod
    def permission_denied(path: str, operation: Optional[str] = None) -> str:
        """Report permission denied error with helpful suggestions.

        Args:
            path: The path that caused permission error
            operation: Optional operation description

        Returns:
            Formatted error message with permission fix suggestions
        """
        op_text = f" during {operation}" if operation else ""
        return (
            f"❌ Permission denied{op_text}: {path}\n"
            f"💡 Try one of these solutions:\n"
            f"   • Check file permissions: ls -la {path}\n"
            f"   • Fix permissions: chmod 755 {path}\n"
            f"   • Run as administrator if needed"
        )

    @staticmethod
    def network_error(operation: str, error_details: Optional[str] = None) -> str:
        """Report network-related errors with connectivity suggestions.

        Args:
            operation: What operation failed (e.g., "downloading package")
            error_details: Optional detailed error message

        Returns:
            Formatted error message with network troubleshooting tips
        """
        base_message = f"❌ Network error during {operation}"
        if error_details:
            base_message += f": {error_details}"

        return (
            f"{base_message}\n"
            f"💡 Network troubleshooting:\n"
            f"   • Check your internet connection\n"
            f"   • Try again in a few minutes\n"
            f"   • Check if a firewall is blocking the connection\n"
            f"   • Verify proxy settings if you're behind a corporate firewall"
        )

    @staticmethod
    def file_not_found(file_path: str, context: Optional[str] = None) -> str:
        """Report file not found error with location suggestions.

        Args:
            file_path: The missing file path
            context: Optional context about what needs this file

        Returns:
            Formatted error message with file location suggestions
        """
        context_text = f" ({context})" if context else ""
        return (
            f"❌ File not found{context_text}: {file_path}\n"
            f"💡 File location tips:\n"
            f"   • Verify the path is correct\n"
            f"   • Check if the file exists: ls -la {file_path}\n"
            f"   • Make sure MYCC is properly installed"
        )

    @staticmethod
    def configuration_error(config_name: str, issue: str) -> str:
        """Report configuration validation errors.

        Args:
            config_name: Name of the configuration
            issue: Description of the issue

        Returns:
            Formatted error message for configuration problems
        """
        return (
            f"❌ Configuration error in {config_name}: {issue}\n"
            f"💡 To fix configuration issues:\n"
            f"   • Check the configuration file format\n"
            f"   • Ensure all required fields are present\n"
            f"   • Verify file paths are correct"
        )

    @staticmethod
    def installation_failed(module_name: str, reason: Optional[str] = None) -> str:
        """Report module installation failure.

        Args:
            module_name: Name of the module that failed to install
            reason: Optional specific reason for failure

        Returns:
            Formatted error message for installation failures
        """
        base_message = f"❌ Failed to install {module_name}"
        if reason:
            base_message += f": {reason}"

        return (
            f"{base_message}\n"
            f"💡 Installation troubleshooting:\n"
            f"   • Check dependencies: mycc deps\n"
            f"   • Verify disk space and permissions\n"
            f"   • Try running the command again\n"
            f"   • Check the status: mycc status"
        )

    @staticmethod
    def generic_error(operation: str, error_message: str) -> str:
        """Report generic errors with basic troubleshooting advice.

        Args:
            operation: What operation was being performed
            error_message: The error message

        Returns:
            Formatted generic error message
        """
        return (
            f"❌ Error during {operation}: {error_message}\n"
            f"💡 General troubleshooting:\n"
            f"   • Try the operation again\n"
            f"   • Check system requirements\n"
            f"   • Verify all dependencies are installed"
        )
