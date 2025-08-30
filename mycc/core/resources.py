"""Resource access utilities for MYCC data files.

This module provides a unified interface for accessing package data files
using importlib.resources, with proper fallback handling for development
and packaged environments.
"""

import json
from typing import Any, Optional
from pathlib import Path
from importlib import resources

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback for Python 3.10


class ResourceAccessError(Exception):
    """Raised when resource access fails in all available methods."""
    pass


def get_data_directory(package_name: str, fallback_path: Optional[Path] = None) -> Path:
    """Get a data directory using importlib.resources with fallback.
    
    Args:
        package_name: The package name (e.g., 'mycc.data.commands')
        fallback_path: Fallback path for development environment
        
    Returns:
        Path to the data directory
        
    Raises:
        ResourceAccessError: If directory cannot be accessed
    """
    # Generate fallback path first
    if fallback_path is None:
        # Determine project root from this file's location
        project_root = Path(__file__).parent.parent.parent
        
        # Convert package name to path
        package_parts = package_name.split('.')
        if package_parts[0] == 'mycc' and len(package_parts) >= 2:
            # e.g., 'mycc.data.commands' -> 'mycc/data/commands'
            fallback_path = project_root.joinpath(*package_parts)
        else:
            raise ResourceAccessError(f"Cannot determine fallback path for package: {package_name}")

    try:
        # Try modern importlib.resources.files() API (Python 3.9+)
        resource_path = resources.files(package_name)
        
        # Handle MultiplexedPath and other resource types
        if hasattr(resource_path, '__fspath__'):
            # For cases where we can get a filesystem path
            resolved_path = Path(resource_path.__fspath__())
            if resolved_path.exists():
                return resolved_path
        
        # For MultiplexedPath or other cases, check if we can iterate
        try:
            # Try to verify the directory exists by listing its contents
            list(resource_path.iterdir())
            # If we can iterate, create a wrapper that works like Path
            return _ResourcePathWrapper(resource_path, fallback_path)
        except (AttributeError, TypeError):
            pass
            
        # Fallback to filesystem path
        if fallback_path and fallback_path.exists():
            return fallback_path
            
    except (ImportError, FileNotFoundError, AttributeError) as e:
        # Use filesystem fallback
        if fallback_path and fallback_path.exists():
            return fallback_path
            
        raise ResourceAccessError(
            f"Failed to access package '{package_name}': {e}\n"
            f"Attempted fallback path '{fallback_path}' does not exist."
        )

    # Final fallback attempt
    if fallback_path and fallback_path.exists():
        return fallback_path
        
    raise ResourceAccessError(
        f"Failed to access package '{package_name}' through all methods.\n"
        f"Attempted fallback path '{fallback_path}' does not exist."
    )


def get_data_file(package_name: str, filename: str, fallback_path: Optional[Path] = None) -> Path:
    """Get a specific data file using importlib.resources with fallback.
    
    Args:
        package_name: The package name (e.g., 'mycc.data.config')
        filename: The filename to access (e.g., 'registry.toml')
        fallback_path: Full fallback path to the file
        
    Returns:
        Path to the data file
        
    Raises:
        ResourceAccessError: If file cannot be accessed
    """
    try:
        # Try modern importlib.resources.files() API
        resource_files = resources.files(package_name)
        file_resource = resource_files / filename
        
        if hasattr(file_resource, 'read_text'):
            # Verify file exists by attempting to get its path
            if hasattr(file_resource, '__fspath__'):
                return Path(file_resource.__fspath__())
            else:
                # For newer versions, we need to use a context manager
                # Return a temporary path that can be used later
                return _create_temp_path_reference(file_resource)
                
    except (ImportError, FileNotFoundError, AttributeError) as e:
        if fallback_path and fallback_path.exists():
            return fallback_path
            
        # Generate fallback path
        if fallback_path is None:
            data_dir = get_data_directory(package_name)
            fallback_path = data_dir / filename
            
        if fallback_path.exists():
            return fallback_path
            
        raise ResourceAccessError(
            f"Failed to access file '{filename}' from package '{package_name}': {e}\n"
            f"Attempted fallback path '{fallback_path}' does not exist."
        )


def read_json_resource(package_name: str, filename: str, fallback_path: Optional[Path] = None) -> Any:
    """Read a JSON file from package resources.
    
    Args:
        package_name: The package name
        filename: The JSON filename
        fallback_path: Fallback file path
        
    Returns:
        Parsed JSON data
        
    Raises:
        ResourceAccessError: If file cannot be read or parsed
    """
    try:
        # Try to read directly from resources
        resource_files = resources.files(package_name)
        json_file = resource_files / filename
        content = json_file.read_text(encoding='utf-8')
        return json.loads(content)
        
    except (ImportError, FileNotFoundError, json.JSONDecodeError) as e:
        # Fall back to filesystem access
        file_path = get_data_file(package_name, filename, fallback_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as fallback_error:
            raise ResourceAccessError(
                f"Failed to read JSON from '{filename}' in package '{package_name}': "
                f"Primary error: {e}, Fallback error: {fallback_error}"
            )


def read_toml_resource(package_name: str, filename: str, fallback_path: Optional[Path] = None) -> Any:
    """Read a TOML file from package resources.
    
    Args:
        package_name: The package name
        filename: The TOML filename
        fallback_path: Fallback file path
        
    Returns:
        Parsed TOML data
        
    Raises:
        ResourceAccessError: If file cannot be read or parsed
    """
    try:
        # Try to read directly from resources
        resource_files = resources.files(package_name)
        toml_file = resource_files / filename
        content = toml_file.read_text(encoding='utf-8')
        return tomllib.loads(content)
        
    except (ImportError, FileNotFoundError, tomllib.TOMLDecodeError) as e:
        # Fall back to filesystem access
        file_path = get_data_file(package_name, filename, fallback_path)
        try:
            with open(file_path, 'rb') as f:
                return tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError) as fallback_error:
            raise ResourceAccessError(
                f"Failed to read TOML from '{filename}' in package '{package_name}': "
                f"Primary error: {e}, Fallback error: {fallback_error}"
            )


def list_resource_files(package_name: str, pattern: str = "*", fallback_path: Optional[Path] = None) -> list[Path]:
    """List files in a resource directory matching a pattern.
    
    Args:
        package_name: The package name
        pattern: Glob pattern for file matching
        fallback_path: Fallback directory path
        
    Returns:
        List of file paths
        
    Raises:
        ResourceAccessError: If directory cannot be accessed
    """
    # Use get_data_directory which handles all the complex resource access logic
    data_dir = get_data_directory(package_name, fallback_path)
    return list(data_dir.glob(pattern))


class _ResourcePathWrapper:
    """Wrapper for importlib.resources that provides Path-like interface.
    
    This handles cases like MultiplexedPath where we can't get a direct filesystem path
    but can still access the resources.
    """
    
    def __init__(self, resource, fallback_path: Path):
        self._resource = resource
        self._fallback_path = fallback_path
        
    def exists(self) -> bool:
        """Check if the resource exists."""
        try:
            list(self._resource.iterdir())
            return True
        except (AttributeError, TypeError, FileNotFoundError):
            return self._fallback_path.exists() if self._fallback_path else False
            
    def glob(self, pattern: str):
        """Glob pattern matching on resources."""
        try:
            # Try resource glob first
            if hasattr(self._resource, 'glob'):
                return list(self._resource.glob(pattern))
        except (AttributeError, TypeError):
            pass
            
        # Try iterdir and manual pattern matching
        try:
            import fnmatch
            files = []
            for item in self._resource.iterdir():
                if fnmatch.fnmatch(item.name, pattern):
                    files.append(item)
            return files
        except (AttributeError, TypeError):
            pass
            
        # Fallback to filesystem
        if self._fallback_path and self._fallback_path.exists():
            return list(self._fallback_path.glob(pattern))
            
        return []
        
    def __truediv__(self, other):
        """Path division operator."""
        try:
            return self._resource / other
        except (AttributeError, TypeError):
            if self._fallback_path:
                return self._fallback_path / other
            raise
            
    def __str__(self):
        return str(self._resource)
        
    def __fspath__(self):
        """Return filesystem path if possible."""
        if hasattr(self._resource, '__fspath__'):
            return self._resource.__fspath__()
        return str(self._fallback_path) if self._fallback_path else str(self._resource)


def _create_temp_path_reference(resource):
    """Create a temporary path reference for newer importlib.resources.
    
    This is a placeholder for cases where we need Path-like access
    to resources that only provide context manager access.
    """
    # For now, this is a simple wrapper that provides basic Path operations
    # In a more complete implementation, this could use tempfile or other mechanisms
    class ResourcePathReference:
        def __init__(self, resource):
            self._resource = resource
            
        def exists(self):
            try:
                self._resource.read_text()
                return True
            except (FileNotFoundError, AttributeError):
                return False
                
        def read_text(self, encoding='utf-8'):
            return self._resource.read_text(encoding=encoding)
            
        @property
        def name(self):
            """Get the name of the resource."""
            if hasattr(self._resource, 'name'):
                return self._resource.name
            return str(self._resource).split('/')[-1]
            
        def __str__(self):
            return str(self._resource)
            
        def __fspath__(self):
            return str(self._resource)
    
    return ResourcePathReference(resource)


# Convenience functions for common MYCC data access patterns

def get_commands_directory() -> Path:
    """Get the commands data directory."""
    return get_data_directory('mycc.data.commands')


def get_config_directory() -> Path:
    """Get the config data directory."""
    return get_data_directory('mycc.data.config')


def get_mcp_config_directory() -> Path:
    """Get the MCP config data directory."""
    return get_data_directory('mycc.data.config.mcp')


def read_registry_toml() -> dict[str, Any]:
    """Read the main configuration registry TOML file."""
    return read_toml_resource('mycc.data.config', 'registry.toml')


def read_mcp_servers_json() -> dict[str, Any]:
    """Read the MCP servers configuration JSON file."""
    return read_json_resource('mycc.data.config.mcp', 'servers.json')


def list_command_files() -> list[Path]:
    """List all command markdown files."""
    return list_resource_files('mycc.data.commands', '*.md')