"""Configs Module - Manages Claude Code configuration files."""

from pathlib import Path
from importlib import resources

from mycc.modules.base import BaseModule


class ConfigsModule(BaseModule):
    """Module for managing Claude Code configurations."""

    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False, home_dir: Path | None = None):
        super().__init__(project_root, target_root, test_mode)
        self.target_dir = target_root
        self.home_dir = home_dir or (Path.cwd() / ".test_home" if test_mode else Path.home())

    def _get_config_path(self) -> Path:
        """Get the path to config data directory."""
        try:
            # Use importlib.resources to get the config directory
            import mycc.data.config
            with resources.path('mycc.data.config', '') as config_path:
                return config_path
        except (ImportError, FileNotFoundError):
            # Fallback to development environment
            return self.project_root / "mycc" / "data" / "config"

    def install(self) -> bool:
        """Install configuration files."""
        try:
            config_dir = self._get_config_path()
            if not config_dir.exists():
                print(f"Config directory not found: {config_dir}")
                return False

            success = True

            # Install Claude settings
            claude_config = config_dir / "claude" / "settings.json"
            if claude_config.exists():
                success &= self._install_claude_settings(claude_config)

            # Install ccstatusline settings
            statusline_config = config_dir / "ccstatusline" / "settings.json"
            if statusline_config.exists():
                success &= self._install_statusline_settings(statusline_config)

            # Install TweakCC settings
            tweakcc_config = config_dir / "tweakcc" / "config.json"
            if tweakcc_config.exists():
                success &= self._install_tweakcc_settings(tweakcc_config)

            return success

        except Exception as e:
            print(f"Error installing configs: {e}")
            return False

    def _install_claude_settings(self, source: Path) -> bool:
        """Install Claude settings.json."""
        try:
            target = self.target_dir / "settings.json"

            # Backup existing file if it exists
            if target.exists() and not target.is_symlink():
                backup = target.with_suffix(".json.backup")
                target.rename(backup)
                print(f"  Backed up existing settings to {backup}")

            # Create symlink
            if target.is_symlink():
                target.unlink()

            target.symlink_to(source.resolve())
            print(f"  + Linked Claude settings.json")
            return True

        except Exception as e:
            print(f"Error installing Claude settings: {e}")
            return False

    def _install_statusline_settings(self, source: Path) -> bool:
        """Install ccstatusline settings.json."""
        try:
            target_dir = self.home_dir / ".config" / "ccstatusline"
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / "settings.json"

            # Backup existing file if it exists
            if target.exists() and not target.is_symlink():
                backup = target.with_suffix(".json.backup")
                target.rename(backup)
                print(f"  Backed up existing ccstatusline settings to {backup}")

            # Create symlink
            if target.is_symlink():
                target.unlink()

            target.symlink_to(source.resolve())
            print(f"  + Linked ccstatusline settings.json")
            return True

        except Exception as e:
            print(f"Error installing ccstatusline settings: {e}")
            return False

    def _install_tweakcc_settings(self, source: Path) -> bool:
        """Install TweakCC config.json."""
        try:
            target_dir = self.home_dir / ".tweakcc"
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / "config.json"

            # Backup existing file if it exists
            if target.exists() and not target.is_symlink():
                backup = target.with_suffix(".json.backup")
                target.rename(backup)
                print(f"  Backed up existing TweakCC config to {backup}")

            # Create symlink
            if target.is_symlink():
                target.unlink()

            target.symlink_to(source.resolve())
            print(f"  + Linked TweakCC config.json")
            return True

        except Exception as e:
            print(f"Error installing TweakCC config: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed configuration files."""
        try:
            success = True

            # Remove Claude settings link
            claude_settings = self.target_dir / "settings.json"
            if claude_settings.is_symlink():
                claude_settings.unlink()
                print("  - Removed Claude settings link")

            # Remove ccstatusline settings link
            statusline_settings = self.home_dir / ".config" / "ccstatusline" / "settings.json"
            if statusline_settings.is_symlink():
                statusline_settings.unlink()
                print("  - Removed ccstatusline settings link")

            # Remove TweakCC config link
            tweakcc_config = self.home_dir / ".tweakcc" / "config.json"
            if tweakcc_config.is_symlink():
                tweakcc_config.unlink()
                print("  - Removed TweakCC config link")

            return success

        except Exception as e:
            print(f"Error uninstalling configs: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if configurations are installed."""
        claude_settings = self.target_dir / "settings.json"
        statusline_settings = self.home_dir / ".config" / "ccstatusline" / "settings.json"
        tweakcc_config = self.home_dir / ".tweakcc" / "config.json"

        # Check if at least one config is linked
        return claude_settings.is_symlink() or statusline_settings.is_symlink() or tweakcc_config.is_symlink()

    def get_description(self) -> str:
        """Get module description."""
        return "Claude Code configuration files"

    def get_install_path(self) -> Path:
        """Get the installation path."""
        return self.target_dir

    def get_files(self) -> list[str]:
        """Get list of config files."""
        files = []
        config_dir = self._get_config_path()
        
        if not config_dir.exists():
            return files

        claude_config = config_dir / "claude" / "settings.json"
        if claude_config.exists():
            files.append("claude/settings.json")

        statusline_config = config_dir / "ccstatusline" / "settings.json"
        if statusline_config.exists():
            files.append("ccstatusline/settings.json")

        tweakcc_config = config_dir / "tweakcc" / "config.json"
        if tweakcc_config.exists():
            files.append("tweakcc/config.json")

        return files