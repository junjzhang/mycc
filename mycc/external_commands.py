"""Unified external command execution with consistent error handling.

This module provides a single, consistent interface for all subprocess operations
across MYCC, eliminating the scattered error handling patterns found in deps.py
and mcp_module.py.
"""

import subprocess
from typing import List, Union, Optional
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of executing an external command.

    This standardizes the return format from all external command executions,
    making error handling consistent across the codebase.
    """

    success: bool
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    command: List[str]

    @property
    def output(self) -> str:
        """Get the primary output (stdout if success, stderr if failure)."""
        return self.stdout if self.success else self.stderr

    @property
    def friendly_error(self) -> Optional[str]:
        """Get user-friendly error message with suggestions."""
        if self.success:
            return None

        # Import here to avoid circular imports
        from mycc.error_reporter import ErrorReporter

        command_str = " ".join(self.command)

        if self.timed_out:
            return ErrorReporter.generic_error("command execution", f"Command timed out: {command_str}")
        elif "not found" in self.stderr or "command not found" in self.stderr:
            return ErrorReporter.subprocess_failed(command_str, "Command not found")
        elif "permission denied" in self.stderr.lower():
            return ErrorReporter.permission_denied(command_str, "command execution")
        else:
            return ErrorReporter.subprocess_failed(command_str, self.stderr or "Unknown error")


class ExternalCommand:
    """Unified executor for external commands with consistent error handling.

    This eliminates the different subprocess patterns scattered across:
    - deps.py: Tool existence checks
    - mcp_module.py: Claude CLI interactions

    Provides consistent timeout handling, error reporting, and logging.
    """

    def run(
        self, cmd: Union[str, List[str]], timeout: int = 30, capture_output: bool = True, text: bool = True
    ) -> CommandResult:
        """Execute an external command with unified error handling.

        Args:
            cmd: Command to execute (string or list of strings)
            timeout: Timeout in seconds (default: 30)
            capture_output: Whether to capture stdout/stderr (default: True)
            text: Whether to return strings instead of bytes (default: True)

        Returns:
            CommandResult with standardized success/failure information
        """
        # Normalize command to list format
        if isinstance(cmd, str):
            command = cmd.split()
        else:
            command = cmd

        try:
            result = subprocess.run(command, capture_output=capture_output, text=text, timeout=timeout)

            return CommandResult(
                success=(result.returncode == 0),
                returncode=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                timed_out=False,
                command=command,
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                timed_out=True,
                command=command,
            )

        except FileNotFoundError:
            return CommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"Command not found: {command[0]}",
                timed_out=False,
                command=command,
            )

        except Exception as e:
            return CommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"Unexpected error: {e}",
                timed_out=False,
                command=command,
            )


# Global instance for easy importing
external_cmd = ExternalCommand()
