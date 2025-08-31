"""Configs sub-module for managing configuration file symbolic links."""

from typing import Any, Dict
from pathlib import Path

from mycc.config import CONFIG_MAPPINGS, get_all_config_keys
from mycc.modules.base_sub_module import BaseSubModule


class ConfigsModule(BaseSubModule):
    """Handles configuration file symbolic linking.

    This module manages the installation of configuration files
    by creating symbolic links from package data to user directories.
    """

    def install(self) -> bool:
        """Install configuration files by creating symbolic links."""
        try:
            success = True
            installed_count = 0

            for config_key in get_all_config_keys():
                try:
                    if self._install_single_config(config_key):
                        installed_count += 1
                    else:
                        success = False
                except Exception as e:
                    print(f"❌ Error installing {config_key}: {e}")
                    success = False

            if installed_count > 0:
                print(f"✅ Installed {installed_count} configuration links")

            return success

        except Exception as e:
            print(f"❌ Error installing configs: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove installed configuration file links."""
        try:
            success = True
            removed_count = 0

            for config_key in get_all_config_keys():
                try:
                    target_path = self.paths.get_config_target_path(config_key)
                    if target_path.is_symlink():
                        target_path.unlink()
                        removed_count += 1
                        config_info = CONFIG_MAPPINGS[config_key]
                        print(f"✅ Removed {config_info['name']} link")
                except Exception as e:
                    print(f"❌ Error removing {config_key}: {e}")
                    success = False

            print(f"✅ Removed {removed_count} configuration links")
            return success

        except Exception as e:
            print(f"❌ Error uninstalling configs: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if configs are installed."""
        for config_key in get_all_config_keys():
            target_path = self.paths.get_config_target_path(config_key)
            if target_path.is_symlink():
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get configs sub-module status."""
        linked_configs = []
        missing_configs = []

        for config_key in get_all_config_keys():
            target_path = self.paths.get_config_target_path(config_key)
            config_info = CONFIG_MAPPINGS[config_key]

            if target_path.is_symlink():
                linked_configs.append(config_info["name"])
            else:
                missing_configs.append(str(target_path))

        installed = len(linked_configs) > 0

        return {
            "installed": installed,
            "linked_count": len(linked_configs),
            "missing_count": len(missing_configs),
            "linked_configs": linked_configs,
            "missing_configs": missing_configs,
            "description": f"{len(linked_configs)} configs linked" if installed else "not installed",
        }

    def get_description(self) -> str:
        """Get human-readable description."""
        return "Configuration file symbolic links"

    def get_install_path(self) -> Path:
        """Get installation path."""
        return self.home_dir

    def _install_single_config(self, config_key: str) -> bool:
        """Install a single configuration file."""
        config_info = CONFIG_MAPPINGS[config_key]

        # Get source and target paths
        source_path = self.paths.get_config_source_path(config_key)
        target_path = self.paths.get_config_target_path(config_key)

        # Check if source exists
        if not source_path.exists():
            print(f"⚠️ Config source not found: {source_path}")
            return False

        # Create target directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle existing target
        if target_path.exists() or target_path.is_symlink():
            if config_info.get("backup_existing", True) and target_path.exists() and not target_path.is_symlink():
                # Create backup of regular file
                backup_path = target_path.with_suffix(target_path.suffix + ".backup")
                target_path.rename(backup_path)
                print(f"📋 Backed up existing {config_info['name']} to {backup_path}")
            else:
                # Remove existing file/symlink
                target_path.unlink()

        # Create symbolic link
        target_path.symlink_to(source_path.resolve())
        print(f"✅ Linked {config_info['name']}")
        return True
