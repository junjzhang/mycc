"""Commands sub-module for managing Claude Code slash commands."""

import shutil
from typing import Any, Dict
from pathlib import Path

from mycc.config import COMMAND_PATTERNS
from mycc.modules.base_sub_module import BaseSubModule


class CommandsModule(BaseSubModule):
    """Handles Claude Code slash commands installation.

    This module manages the installation of .md command files
    to the ~/.claude/commands/ directory.
    """

    def __init__(self, claude_dir: Path, home_dir: Path, data_dir: Path):
        super().__init__(claude_dir, home_dir, data_dir)
        # Use centralized path management - no need to calculate paths manually

    def install(self) -> bool:
        """Install command files to ~/.claude/commands/."""
        try:
            commands_source_dir = self.paths.commands_data_dir

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
            self.paths.commands_dir.mkdir(parents=True, exist_ok=True)

            # Copy all command files
            copied_count = 0
            for cmd_file in command_files:
                try:
                    target_file = self.paths.commands_dir / cmd_file.name
                    shutil.copy2(cmd_file, target_file)
                    copied_count += 1
                except Exception as e:
                    print(f"❌ Failed to copy {cmd_file.name}: {e}")
                    continue

            if copied_count > 0:
                print(f"✅ Installed {copied_count} commands to {self.paths.commands_dir}")
                return True
            else:
                print("❌ Failed to install any command files")
                return False

        except Exception as e:
            print(f"❌ Error installing commands: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed command files."""
        try:
            if not self.paths.commands_dir.exists():
                print("✅ Commands already uninstalled")
                return True

            removed_count = 0
            for pattern in COMMAND_PATTERNS:
                for cmd_file in self.paths.commands_dir.glob(pattern):
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

    def is_installed(self) -> bool:
        """Check if commands are installed."""
        if not self.paths.commands_dir.exists():
            return False

        # Check if there are any command files
        for pattern in COMMAND_PATTERNS:
            if list(self.paths.commands_dir.glob(pattern)):
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get commands sub-module status."""
        installed = self.is_installed()
        file_count = 0

        if installed:
            for pattern in COMMAND_PATTERNS:
                file_count += len(list(self.paths.commands_dir.glob(pattern)))

        return {
            "installed": installed,
            "file_count": file_count,
            "path": str(self.paths.commands_dir),
            "description": f"{file_count} command files" if installed else "not installed",
        }

    def get_description(self) -> str:
        """Get human-readable description."""
        return "Claude Code slash commands (.md files)"

    def get_install_path(self) -> Path:
        """Get installation path."""
        return self.paths.commands_dir
