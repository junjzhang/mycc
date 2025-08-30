"""Commands Module - Manages Claude Code command files."""
import shutil
from pathlib import Path

from mycc.modules.base import BaseModule
from mycc.core.resources import get_commands_directory, list_command_files, ResourceAccessError


class CommandsModule(BaseModule):
    """Module for managing Claude Code commands."""

    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False):
        super().__init__(project_root, target_root, test_mode)
        self.target_dir = self.target_root / "commands"

    def _get_commands_path(self) -> Path:
        """Get the path to commands data directory."""
        try:
            return get_commands_directory()
        except ResourceAccessError as e:
            # Fallback to development path
            fallback_path = self.project_root / "mycc" / "data" / "commands"
            if fallback_path.exists():
                return fallback_path
            # Re-raise with more context if fallback also fails
            raise ResourceAccessError(
                f"Failed to access commands directory: {e}\n"
                f"Fallback path '{fallback_path}' also does not exist."
            )

    def install(self) -> bool:
        """Install command files to ~/.claude/commands/."""
        try:
            # Use unified resource access to get command files
            command_files = list_command_files()
            if not command_files:
                print("No command files found in package resources")
                return False

            # Ensure target directory exists
            self.target_dir.mkdir(parents=True, exist_ok=True)

            # Copy all command files
            copied_count = 0
            for cmd_file in command_files:
                try:
                    target_file = self.target_dir / cmd_file.name
                    # Handle both Path objects and resource references
                    if hasattr(cmd_file, 'read_text'):
                        # Resource reference - read content and write to target
                        content = cmd_file.read_text(encoding='utf-8')
                        target_file.write_text(content, encoding='utf-8')
                    else:
                        # Regular Path object - use standard copy
                        shutil.copy2(cmd_file, target_file)
                    print(f"  + {cmd_file.name}")
                    copied_count += 1
                except Exception as e:
                    print(f"  ! Failed to copy {cmd_file.name}: {e}")
                    continue

            if copied_count > 0:
                print(f"Installed {copied_count} commands to {self.target_dir}")
                return True
            else:
                print("Failed to install any command files")
                return False

        except Exception as e:
            print(f"Error installing commands: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed command files."""
        try:
            if not self.target_dir.exists():
                return True  # Already uninstalled

            # Get list of our command files using unified resource access
            try:
                command_files = list_command_files()
                source_files = set(f.name for f in command_files)
            except ResourceAccessError:
                # If we can't access resources, remove all .md files in target
                source_files = set(f.name for f in self.target_dir.glob("*.md"))

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

        try:
            # Use unified resource access to get command files
            command_files = list_command_files()
            source_files = set(f.name for f in command_files)
        except ResourceAccessError:
            # If resource access fails, assume not installed
            return False

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
        try:
            command_files = list_command_files()
            return [f.name for f in command_files]
        except ResourceAccessError:
            # If resource access fails, return empty list
            return []