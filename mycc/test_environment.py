"""Unified test environment manager for MYCC.

This module centralizes test mode detection and directory management,
eliminating the duplicate MYCC_TEST_MODE checks scattered across cli.py and manager.py.
"""

import os
from typing import Tuple, Optional
from pathlib import Path


class TestEnvironment:
    """Centralized test environment management.

    Single source of truth for test mode detection and test directory paths.
    Follows Linus principle: one place to control test behavior.
    """

    @staticmethod
    def is_test_mode() -> bool:
        """Check if running in test mode.

        Returns:
            True if MYCC_TEST_MODE environment variable is set
        """
        return bool(os.getenv("MYCC_TEST_MODE", ""))

    @staticmethod
    def get_test_directories() -> Tuple[Path, Path]:
        """Get test mode directories.

        Returns:
            Tuple of (claude_dir, home_dir) for test mode
        """
        base_dir = Path.cwd()
        return (base_dir / ".test_claude", base_dir / ".test_home")

    @classmethod
    def get_manager_paths(cls) -> Tuple[Optional[Path], Optional[Path]]:
        """Get paths for ModuleManager initialization.

        Returns:
            Tuple of (claude_dir, home_dir) - None values for production mode
        """
        if cls.is_test_mode():
            return cls.get_test_directories()
        else:
            return (None, None)

    @classmethod
    def print_test_mode_info(cls) -> None:
        """Print test mode information if in test mode."""
        if cls.is_test_mode():
            print("🧪 Using test mode with temporary directories")
