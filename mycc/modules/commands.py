"""Commands Module - Manages Claude Code command files."""

import shutil
from pathlib import Path
from importlib import resources

from mycc.modules.base import BaseModule


class CommandsModule(BaseModule):
    """Module for managing Claude Code commands."""

    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False):
        super().__init__(project_root, target_root, test_mode)
        self.target_dir = self.target_root / "commands"

    def _get_commands_path(self) -> Path:
        """Get the path to commands data directory."""
        try:
            # Use importlib.resources to get the commands directory
            import mycc.data.commands
            with resources.path('mycc.data.commands', '') as commands_path:
                return commands_path
        except (ImportError, FileNotFoundError):
            # Fallback to development environment
            return self.project_root / "mycc" / "data" / "commands"

    def install(self) -> bool:
        """Install command files to ~/.claude/commands/."""
        try:
            source_dir = self._get_commands_path()
            
            if not source_dir.exists():
                print(f"Commands source directory not found: {source_dir}")
                return False

            # Ensure target directory exists
            self.target_dir.mkdir(parents=True, exist_ok=True)

            # Copy all .md files
            command_files = list(source_dir.glob("*.md"))
            if not command_files:
                print(f"No command files found in {source_dir}")
                return False

            for cmd_file in command_files:
                target_file = self.target_dir / cmd_file.name
                shutil.copy2(cmd_file, target_file)
                print(f"  + {cmd_file.name}")

            print(f"Installed {len(command_files)} commands to {self.target_dir}")
            return True

        except Exception as e:
            print(f"Error installing commands: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed command files."""
        try:
            if not self.target_dir.exists():
                return True  # Already uninstalled

            # Get list of our command files
            source_dir = self._get_commands_path()
            source_files = set(f.name for f in source_dir.glob("*.md")) if source_dir.exists() else set()

            removed_count = 0
            for cmd_file in self.target_dir.glob("*.md"):
                if cmd_file.name in source_files:
                    cmd_file.unlink()
                    print(f"  - {cmd_file.name}")
                    removed_count += 1

            print(f"Removed {removed_count} commands from {self.target_dir}")
            return True

        except Exception as e:
            print(f"Error uninstalling commands: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if commands are installed."""
        if not self.target_dir.exists():
            return False

        source_dir = self._get_commands_path()
        if not source_dir.exists():
            return False

        source_files = set(f.name for f in source_dir.glob("*.md"))
        target_files = set(f.name for f in self.target_dir.glob("*.md"))

        # Check if at least some of our commands are installed
        return len(source_files.intersection(target_files)) > 0

    def get_description(self) -> str:
        """Get module description."""
        return "Claude Code slash commands"

    def get_install_path(self) -> Path:
        """Get the installation path."""
        return self.target_dir

    def get_files(self) -> list[str]:
        """Get list of command files."""
        source_dir = self._get_commands_path()
        if not source_dir.exists():
            return []

        return [f.name for f in source_dir.glob("*.md")]