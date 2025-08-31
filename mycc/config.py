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
    """Get the source path for a configuration file."""
    config_info = CONFIG_MAPPINGS.get(config_key)
    if not config_info:
        raise ValueError(f"Unknown config key: {config_key}")

    return data_dir / "config" / config_info["source"]


def get_config_target_path(config_key: str, home_dir: Path) -> Path:
    """Get the target path for a configuration file."""
    config_info = CONFIG_MAPPINGS.get(config_key)
    if not config_info:
        raise ValueError(f"Unknown config key: {config_key}")

    if config_info["relative_to_home"]:
        return home_dir / config_info["target"]
    else:
        return Path(config_info["target"])


def get_all_config_keys() -> list[str]:
    """Get all available configuration keys."""
    return list(CONFIG_MAPPINGS.keys())


def get_all_mcp_server_keys() -> list[str]:
    """Get all available MCP server keys."""
    return list(MCP_SERVERS.keys())


def get_mcp_server_info(server_key: str) -> dict:
    """Get MCP server information."""
    return MCP_SERVERS.get(server_key, {})
