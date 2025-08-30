"""Configs Module - Manages Claude Code configuration files."""

from pathlib import Path

from mycc.core.logger import get_logger
from mycc.modules.base import BaseModule
from mycc.core.resources import ResourceAccessError, get_config_directory
from mycc.modules.config_registry import ConfigEntry, ConfigRegistry, ConfigRegistryError


class ConfigsModule(BaseModule):
    """Module for managing Claude Code configurations."""

    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False, home_dir: Path | None = None):
        super().__init__(project_root, target_root, test_mode)
        self.target_dir = target_root
        self.home_dir = home_dir or (Path.cwd() / ".test_home" if test_mode else Path.home())
        self.registry = ConfigRegistry()
        self.logger = get_logger()

    def _get_config_path(self) -> Path:
        """Get the path to config data directory."""
        try:
            return get_config_directory()
        except ResourceAccessError as e:
            # Fallback to development path
            fallback_path = self.project_root / "mycc" / "data" / "config"
            if fallback_path.exists():
                return fallback_path
            # Re-raise with more context if fallback also fails
            raise ResourceAccessError(
                f"Failed to access config directory: {e}\nFallback path '{fallback_path}' also does not exist."
            ) from e

    def install(self) -> bool:
        """Install configuration files."""
        try:
            config_base_dir = self._get_config_path()
        except ResourceAccessError as e:
            self.logger.error(f"Error accessing config directory: {e}")
            return False

        try:
            entries = self.registry.get_all_entries()

            success = True
            for name, entry in entries.items():
                try:
                    success &= self._install_config_entry(entry, config_base_dir)
                except Exception as e:
                    self.logger.error(f"Error installing {name}: {e}")
                    success = False

            return success

        except ConfigRegistryError as e:
            self.logger.error(f"Configuration registry error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error installing configs: {e}")
            return False

    def _install_config_entry(self, entry: ConfigEntry, config_base_dir: Path) -> bool:
        """Install a single configuration entry."""
        try:
            # Get source and target paths
            source = entry.get_source_path(config_base_dir)
            if not source.exists():
                if entry.required:
                    self.logger.warning(f"Required config file not found: {source}")
                    return False
                else:
                    self.logger.info(f"Skipping optional config: {source}")
                    return True

            target = entry.get_target_path(self.home_dir, self.target_dir)

            # Create target directory if needed
            if entry.create_dirs:
                target.parent.mkdir(parents=True, exist_ok=True)

            # Handle existing files/symlinks
            if target.exists() or target.is_symlink():
                if target.is_symlink():
                    # Remove existing symlink
                    target.unlink()
                else:
                    # Handle regular file
                    if entry.backup_existing:
                        backup = target.with_suffix(target.suffix + ".backup")
                        target.rename(backup)
                        self.logger.info(f"Backed up existing {entry.name} to {backup}")
                    else:
                        # Remove without backup
                        target.unlink()

            # Create new symlink
            target.symlink_to(source.resolve())
            self.logger.success(f"Linked {entry.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error installing {entry.name}: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed configuration files."""
        try:
            entries = self.registry.get_all_entries()

            success = True
            for entry in entries.values():
                try:
                    target = entry.get_target_path(self.home_dir, self.target_dir)
                    if target.is_symlink():
                        target.unlink()
                        self.logger.success(f"Removed {entry.name} link")
                except Exception as e:
                    self.logger.error(f"Error uninstalling {entry.name}: {e}")
                    success = False

            return success

        except ConfigRegistryError as e:
            self.logger.error(f"Configuration registry error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error uninstalling configs: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if configurations are installed."""
        try:
            entries = self.registry.get_all_entries()

            # Check if at least one config is linked
            for entry in entries.values():
                target = entry.get_target_path(self.home_dir, self.target_dir)
                if target.is_symlink():
                    return True
            return False

        except (ConfigRegistryError, Exception):
            # Fallback to false if registry loading fails
            return False

    def get_description(self) -> str:
        """Get module description."""
        return "Claude Code configuration files"

    def get_install_path(self) -> Path:
        """Get the installation path."""
        return self.target_dir

    def get_files(self) -> list[str]:
        """Get list of config files."""
        try:
            entries = self.registry.get_all_entries()
            config_base_dir = self._get_config_path()

            files = []
            for entry in entries.values():
                source = entry.get_source_path(config_base_dir)
                if source.exists():
                    files.append(entry.source_path)

            return files

        except (ConfigRegistryError, ResourceAccessError, Exception):
            # Fallback to empty list if registry loading fails
            return []
