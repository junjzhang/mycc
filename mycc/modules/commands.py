"""
Commands Module - Manages Claude Code command files
"""

import shutil
from pathlib import Path

from mycc.modules.base import BaseModule


class CommandsModule(BaseModule):
    """Module for managing Claude Code commands"""
    
    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False):
        super().__init__(project_root, target_root, test_mode)
        self.source_dir = self.project_root / "commands"
        self.target_dir = self.target_root / "commands"
    
    def install(self) -> bool:
        """Install command files to ~/.claude/commands/"""
        try:
            if not self.source_dir.exists():
                print(f"Commands source directory not found: {self.source_dir}")
                return False
            
            # Ensure target directory exists
            self.target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all .md files
            command_files = list(self.source_dir.glob("*.md"))
            if not command_files:
                print(f"No command files found in {self.source_dir}")
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
        """Remove installed command files"""
        try:
            if not self.target_dir.exists():
                return True  # Already uninstalled
            
            # Get list of our command files
            source_files = set(f.name for f in self.source_dir.glob("*.md")) if self.source_dir.exists() else set()
            
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
        """Check if commands are installed"""
        if not self.target_dir.exists() or not self.source_dir.exists():
            return False
        
        source_files = set(f.name for f in self.source_dir.glob("*.md"))
        target_files = set(f.name for f in self.target_dir.glob("*.md"))
        
        # Check if at least some of our commands are installed
        return len(source_files.intersection(target_files)) > 0
    
    def get_description(self) -> str:
        """Get module description"""
        return "Claude Code slash commands"
    
    def get_install_path(self) -> Path:
        """Get the installation path"""
        return self.target_dir
    
    def get_files(self) -> list[str]:
        """Get list of command files"""
        if not self.source_dir.exists():
            return []
        
        return [f.name for f in self.source_dir.glob("*.md")]