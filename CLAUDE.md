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

Configs in `mycc/data/config/` are symbolically linked with automatic backup:
- `mycc/data/config/claude/settings.json` → `~/.claude/settings.json`
- `mycc/data/config/ccstatusline/settings.json` → `~/.config/ccstatusline/settings.json`
- `mycc/data/config/tweakcc/config.json` → `~/.tweakcc/config.json`

## Data Files Management

MYCC uses a package-internal data structure:
- **Commands**: 25 slash commands stored in `mycc/data/commands/`
- **Configs**: Configuration templates in `mycc/data/config/`
- **Access**: Uses `importlib.resources` for reliable data file access
- **Packaging**: Data files are included in the wheel/conda package

## MCP Server Management

MCP (Model Context Protocol) servers provide enhanced capabilities:
- **context7**: Document analysis and context management

Installed via `claude mcp add` commands with user scope.

## Packaging & Distribution

MYCC is distributed as conda packages with two variants:
- **Basic (`mycc`)**: Core functionality only
- **Full (`mycc-full`)**: Includes Node.js and npm dependencies

### Building Packages
```bash
# Build both variants
pixi run -e build build-all

# Build specific variant
pixi run -e build build-basic
pixi run -e build build-full

# Clean build artifacts
pixi run -e build clean-build
```

### Installation
```bash
# Install from conda-forge (when published)
pixi global install mycc

# Install from local build
pixi global install --channel conda-forge --channel ./output mycc
```

## Important Notes

- Always use test mode (`--test-mode` or `MYCC_TEST_MODE=1`) for development
- CLI uses Union types for Tyro subcommands, not `tyro.conf.subcommand`
- All modules extend BaseModule with test mode support
- Data files are accessed via `importlib.resources` for packaging compatibility
- Packages are built as `noarch` for cross-platform compatibility
- Run any python command with `pixi run <command>`
- Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks