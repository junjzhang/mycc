"""Configuration Registry - Manages configuration entries and installation rules."""

import threading
from typing import Any, Set, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback for Python 3.10
from importlib import resources


@dataclass
class ConfigEntry:
    """Configuration entry with installation metadata."""

    name: str
    source_path: str
    target_path: str
    relative_to_home: bool = False
    relative_to_config: bool = False
    backup_existing: bool = True
    create_dirs: bool = True
    required: bool = True
    description: str = ""

    def get_target_path(self, home_dir: Path, config_dir: Path) -> Path:
        """Get the resolved target path based on configuration."""
        if self.relative_to_home:
            return home_dir / self.target_path
        elif self.relative_to_config:
            return config_dir / self.target_path
        else:
            return Path(self.target_path)

    def get_source_path(self, config_base_dir: Path) -> Path:
        """Get the resolved source path."""
        return config_base_dir / self.source_path


class ConfigRegistryError(Exception):
    """Exception raised for configuration registry errors."""

    pass


class ConfigValidationError(ConfigRegistryError):
    """Exception raised for configuration validation errors."""

    pass


class ConfigRegistry:
    """Singleton registry for managing configuration entries with caching."""

    _instance: Optional["ConfigRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ConfigRegistry":
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Avoid re-initialization in singleton
        if hasattr(self, "_initialized"):
            return

        self._entries: Dict[str, ConfigEntry] = {}
        self._loaded = False
        self._toml_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
        self._initialized = True

    def _validate_config_data(self, name: str, config_data: Dict[str, Any]) -> None:
        """Validate configuration entry data."""
        required_fields = {"source_path", "target_path"}
        missing_fields = required_fields - set(config_data.keys())

        if missing_fields:
            raise ConfigValidationError(f"Configuration '{name}' missing required fields: {missing_fields}")

        # Validate path formats
        source_path = config_data["source_path"]
        target_path = config_data["target_path"]

        if not isinstance(source_path, str) or not source_path.strip():
            raise ConfigValidationError(f"Invalid source_path for '{name}': must be non-empty string")

        if not isinstance(target_path, str) or not target_path.strip():
            raise ConfigValidationError(f"Invalid target_path for '{name}': must be non-empty string")

        # Validate boolean fields
        bool_fields = ["relative_to_home", "relative_to_config", "backup_existing", "create_dirs", "required"]
        for field in bool_fields:
            if field in config_data and not isinstance(config_data[field], bool):
                raise ConfigValidationError(f"Field '{field}' for '{name}' must be boolean")

        # Validate mutual exclusivity
        if config_data.get("relative_to_home") and config_data.get("relative_to_config"):
            raise ConfigValidationError(
                f"Configuration '{name}' cannot be both relative_to_home and relative_to_config"
            )

    def _load_toml_with_cache(self, toml_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load TOML data with caching."""
        cache_key = str(toml_path) if toml_path else "default"

        with self._cache_lock:
            if cache_key in self._toml_cache:
                return self._toml_cache[cache_key]

        # Load TOML data
        if toml_path is None:
            # Load directly from package resources
            try:
                import mycc.data.config as config_module

                config_files = resources.files(config_module)
                registry_file = config_files / "registry.toml"
                toml_content = registry_file.read_text(encoding="utf-8")
                data = tomllib.loads(toml_content)
            except (ImportError, FileNotFoundError) as e:
                # Fallback to file system
                project_root = Path(__file__).parent.parent.parent
                fallback_path = project_root / "mycc" / "data" / "config" / "registry.toml"
                if not fallback_path.exists():
                    raise ConfigRegistryError(f"Registry file not found: {e}") from e
                with open(fallback_path, "rb") as f:
                    data = tomllib.load(f)
        else:
            # Handle explicit path
            if not toml_path.exists():
                raise ConfigRegistryError(f"Registry file not found: {toml_path}")
            try:
                with open(toml_path, "rb") as f:
                    data = tomllib.load(f)
            except Exception as e:
                raise ConfigRegistryError(f"Failed to parse TOML file {toml_path}: {e}") from e

        # Cache the loaded data
        with self._cache_lock:
            self._toml_cache[cache_key] = data

        return data

    def load_from_toml(self, toml_path: Optional[Path] = None) -> None:
        """Load configuration entries from TOML file with validation."""
        try:
            data = self._load_toml_with_cache(toml_path)
        except Exception as e:
            raise ConfigRegistryError(f"Failed to load configuration: {e}") from e

        configs = data.get("configs", {})
        if not configs:
            raise ConfigRegistryError("No configurations found in registry file")

        # Clear existing entries before loading new ones
        self._entries.clear()

        # Validate and load each configuration
        for name, config_data in configs.items():
            try:
                self._validate_config_data(name, config_data)

                entry = ConfigEntry(
                    name=name,
                    source_path=config_data["source_path"],
                    target_path=config_data["target_path"],
                    relative_to_home=config_data.get("relative_to_home", False),
                    relative_to_config=config_data.get("relative_to_config", False),
                    backup_existing=config_data.get("backup_existing", True),
                    create_dirs=config_data.get("create_dirs", True),
                    required=config_data.get("required", True),
                    description=config_data.get("description", ""),
                )
                self._entries[name] = entry

            except ConfigValidationError as e:
                raise ConfigRegistryError(f"Configuration validation failed: {e}") from e

        self._loaded = True

    def _get_default_registry_path(self) -> Path:
        """Get the path to the default registry TOML file."""
        try:
            # Use importlib.resources to get the registry file
            import mycc.data.config as config_module

            config_files = resources.files(config_module)
            registry_path = config_files / "registry.toml"
            if hasattr(registry_path, "__fspath__"):
                return Path(registry_path.__fspath__())
            else:
                # For older Python versions, extract the path
                return Path(str(registry_path))
        except (ImportError, FileNotFoundError):
            # Fallback for development environment
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            return project_root / "mycc" / "data" / "config" / "registry.toml"

    def _ensure_loaded(self) -> None:
        """Ensure configuration is loaded."""
        if not self._loaded:
            self.load_from_toml()

    def get_all_entries(self) -> Dict[str, ConfigEntry]:
        """Get all configuration entries."""
        self._ensure_loaded()
        return self._entries.copy()

    def get_entry(self, name: str) -> Optional[ConfigEntry]:
        """Get a specific configuration entry by name."""
        self._ensure_loaded()
        return self._entries.get(name)

    def get_required_entries(self) -> Dict[str, ConfigEntry]:
        """Get only required configuration entries."""
        self._ensure_loaded()
        return {name: entry for name, entry in self._entries.items() if entry.required}

    def get_optional_entries(self) -> Dict[str, ConfigEntry]:
        """Get only optional configuration entries."""
        self._ensure_loaded()
        return {name: entry for name, entry in self._entries.items() if not entry.required}

    def get_entries_by_type(
        self, relative_to_home: Optional[bool] = None, relative_to_config: Optional[bool] = None
    ) -> Dict[str, ConfigEntry]:
        """Get configuration entries filtered by type."""
        self._ensure_loaded()
        entries = {}
        for name, entry in self._entries.items():
            if (relative_to_home is None or entry.relative_to_home == relative_to_home) and (
                relative_to_config is None or entry.relative_to_config == relative_to_config
            ):
                entries[name] = entry
        return entries

    def add_entry(self, entry: ConfigEntry) -> None:
        """Add a configuration entry to the registry."""
        if not isinstance(entry, ConfigEntry):
            raise ValueError("entry must be a ConfigEntry instance")
        self._entries[entry.name] = entry

    def remove_entry(self, name: str) -> bool:
        """Remove a configuration entry from the registry."""
        if name in self._entries:
            del self._entries[name]
            return True
        return False

    def has_entry(self, name: str) -> bool:
        """Check if a configuration entry exists."""
        self._ensure_loaded()
        return name in self._entries

    def get_entry_names(self) -> Set[str]:
        """Get all configuration entry names."""
        self._ensure_loaded()
        return set(self._entries.keys())

    def clear_cache(self) -> None:
        """Clear the TOML cache and force reload on next access."""
        with self._cache_lock:
            self._toml_cache.clear()
        self._loaded = False
        self._entries.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for debugging."""
        with self._cache_lock:
            return {
                "loaded": self._loaded,
                "entries_count": len(self._entries),
                "cache_keys": list(self._toml_cache.keys()),
                "cache_size": len(self._toml_cache),
            }

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset singleton instance (useful for testing)."""
        with cls._lock:
            cls._instance = None
