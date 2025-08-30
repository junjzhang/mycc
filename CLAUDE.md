# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MYCC is a modular Claude Code configuration manager built with Python 3.10+. Uses Pixi for dependency management, Tyro+Pydantic for CLI, and PEP 585 type hints.

## Architecture

- **ConfigManager** (`mycc/core/manager.py`): Central orchestrator
- **BaseModule** (`mycc/modules/base.py`): Abstract base for commands/configs/mcp modules
- **Test Mode**: Uses `.test_claude/.test_home` directories for safe development

## Key Commands

```bash
# Installation
pixi run install             # Install all modules  
pixi run status              # Show installation status

# Module-specific installation
python -m mycc install --modules commands,configs,mcp
python -m mycc install --modules mcp --test-mode

# Development
pixi run dev-test            # Full test suite with auto-cleanup
pixi run lint                # Ruff check (dev environment)
pixi run format              # Ruff format (dev environment)

# Testing
python -m mycc install --all --test-mode
MYCC_TEST_MODE=1 python -m mycc status
```

## Configuration Management

Configs in `config/` are symbolically linked with automatic backup:
- `config/claude/settings.json` → `~/.claude/settings.json`
- `config/ccstatusline/settings.json` → `~/.config/ccstatusline/settings.json`
- `config/tweakcc/config.json` → `~/.tweakcc/config.json`

## MCP Server Management

MCP (Model Context Protocol) servers provide enhanced capabilities:
- **context7**: Document analysis and context management

Installed via `claude mcp add` commands with user scope.

## Important Notes

- Always use test mode (`--test-mode` or `MYCC_TEST_MODE=1`) for development
- CLI uses Union types for Tyro subcommands, not `tyro.conf.subcommand`
- All modules extend BaseModule with test mode support
- Run any python command with `pixi run <command>`
- Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks