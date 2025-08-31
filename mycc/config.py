"""Static configuration for MYCC.

This module contains all configuration mappings and settings in simple Python data structures,
replacing the complex TOML-based ConfigRegistry system.
"""

from pathlib import Path

# Configuration file mappings
CONFIG_MAPPINGS = {
    "claude_settings": {
        "name": "Claude Settings",
        "source": "claude/settings.json",
        "target": ".claude/settings.json",
        "relative_to_home": True,
        "backup_existing": True,
        "description": "Main Claude Code settings",
    },
    "ccstatusline_settings": {
        "name": "CCStatusLine Settings",
        "source": "ccstatusline/settings.json",
        "target": ".config/ccstatusline/settings.json",
        "relative_to_home": True,
        "backup_existing": True,
        "description": "CCStatusLine configuration",
    },
    "tweakcc_config": {
        "name": "TweakCC Config",
        "source": "tweakcc/config.json",
        "target": ".tweakcc/config.json",
        "relative_to_home": True,
        "backup_existing": True,
        "description": "TweakCC plugin configuration",
    },
}

# MCP Server configurations
MCP_SERVERS = {
    "context7": {
        "name": "Context7",
        "package": "npx -y @upstash/context7-mcp",
        "description": "Context7 MCP server for enhanced context management with AI-powered document analysis",
        "scope": "user",
        "features": [
            "Document indexing and search",
            "Context-aware responses",
            "Large document processing",
            "Vector embeddings",
        ],
    }
}

# Command file patterns
COMMAND_PATTERNS = ["*.md"]


def get_config_source_path(config_key: str, data_dir: Path) -> Path:
    """Get the source path for a configuration file.

    DEPRECATED: Use PathManager.get_config_source_path() instead.
    This function is kept for backward compatibility only.
    """
    from mycc.path_manager import PathManager

    path_manager = PathManager(data_dir=data_dir)
    return path_manager.get_config_source_path(config_key)


def get_config_target_path(config_key: str, home_dir: Path) -> Path:
    """Get the target path for a configuration file.

    DEPRECATED: Use PathManager.get_config_target_path() instead.
    This function is kept for backward compatibility only.
    """
    from mycc.path_manager import PathManager

    path_manager = PathManager(home_dir=home_dir)
    return path_manager.get_config_target_path(config_key)


def get_all_config_keys() -> list[str]:
    """Get all available configuration keys."""
    return list(CONFIG_MAPPINGS.keys())


def get_all_mcp_server_keys() -> list[str]:
    """Get all available MCP server keys."""
    return list(MCP_SERVERS.keys())


def get_mcp_server_info(server_key: str) -> dict:
    """Get MCP server information."""
    return MCP_SERVERS.get(server_key, {})


def validate_config(data_dir: Path) -> list[str]:
    """Validate configuration completeness at startup.

    Args:
        data_dir: Package data directory path

    Returns:
        List of error messages (empty if all valid)
    """
    errors = []

    # Check CONFIG_MAPPINGS source files exist
    config_data_dir = data_dir / "config"
    for config_key, config_info in CONFIG_MAPPINGS.items():
        source_path = config_data_dir / config_info["source"]
        if not source_path.exists():
            errors.append(f"Config source missing for '{config_key}': {source_path}")

    # Check MCP_SERVERS definitions are complete
    required_mcp_fields = ["name", "package", "description"]
    for server_key, server_info in MCP_SERVERS.items():
        missing_fields = [field for field in required_mcp_fields if field not in server_info]
        if missing_fields:
            errors.append(f"MCP server '{server_key}' missing fields: {missing_fields}")

    return errors


def validate_commands(data_dir: Path) -> list[str]:
    """Validate command files exist.

    Args:
        data_dir: Package data directory path

    Returns:
        List of error messages (empty if all valid)
    """
    errors = []

    commands_dir = data_dir / "commands"
    if not commands_dir.exists():
        errors.append(f"Commands directory missing: {commands_dir}")
        return errors

    # Check if any command files exist
    command_files = []
    for pattern in COMMAND_PATTERNS:
        command_files.extend(commands_dir.glob(pattern))

    if not command_files:
        errors.append(f"No command files found matching patterns: {COMMAND_PATTERNS}")

    return errors


def validate_all(data_dir: Path) -> list[str]:
    """Validate all configurations and data files.

    Args:
        data_dir: Package data directory path

    Returns:
        List of all validation errors (empty if everything is valid)
    """
    errors = []
    errors.extend(validate_config(data_dir))
    errors.extend(validate_commands(data_dir))
    return errors
