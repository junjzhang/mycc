# MCP Configuration

This directory contains configuration templates for Model Context Protocol (MCP) servers.

## Available MCP Servers

### Context7
- **Package**: `@upstash/context7-mcp`
- **Description**: Enhanced context management with AI-powered document analysis
- **Features**: Document indexing, context-aware responses, vector embeddings

## Installation

MCP servers are installed using the MYCC MCP module:

```bash
# Install all MCP servers
pixi run install --modules mcp

# Or use direct Python command
python -m mycc install --modules mcp

# Test mode (safe for development)
python -m mycc install --modules mcp --test-mode
```

## Configuration

MCP servers are installed with user scope and managed through Claude Code's MCP system. Configuration is handled automatically during installation.

## Custom MCP Servers

To add custom MCP servers, modify the `servers.json` file and update the `MCPModule.MCP_SERVERS` dictionary in `mycc/modules/mcp.py`.