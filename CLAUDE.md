# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MYCC is a modular Claude Code configuration manager built with Python 3.10+. Uses Pixi for dependency management, Hatchling+Hatch-VCS for modern packaging, Tyro+Pydantic for CLI, and PEP 585 type hints.

## Architecture

**KISS Simplified 3-Layer Architecture:**
- **CLI** (`mycc/cli.py`): Simple Pydantic+Tyro interface with environment-based test mode
- **ModuleManager** (`mycc/manager.py`): Dependency injection-based module orchestrator
- **Modules**: Only 2 modules - `deps` (dependency checker) and `claude_user_setting` (commands/configs/mcp)
- **Static Config** (`mycc/config.py`): Simple Python dictionaries replacing complex TOML parsing
- **Test Mode**: Uses dependency injection with `MYCC_TEST_MODE=1` environment variable

## Key Commands

```bash
# Installation
pixi run install             # Install all modules  
pixi run status              # Show installation status

# Module-specific installation (new syntax)
python -m mycc install --modules claude_user_setting:commands,configs
python -m mycc install --modules claude_user_setting:mcp
python -m mycc install --modules deps

# Development
pixi run -e dev integration-test  # CLI integration tests (pytest)
pixi run -e dev unit-test         # Unit tests with mocking (pytest)
pixi run -e dev test              # All tests
pixi run lint                     # Ruff check (dev environment)
pixi run format                   # Ruff format (dev environment)

# Testing with Environment Variable
MYCC_TEST_MODE=1 python -m mycc install --all
MYCC_TEST_MODE=1 python -m mycc status
```

## Configuration Management

Configs in `mycc/data/config/` are symbolically linked with automatic backup:
- `mycc/data/config/claude/settings.json` → `~/.claude/settings.json`
- `mycc/data/config/ccstatusline/settings.json` → `~/.config/ccstatusline/settings.json`
- `mycc/data/config/tweakcc/config.json` → `~/.tweakcc/config.json`

## Data Files Management

MYCC uses a package-internal data structure with dependency injection:
- **Commands**: 25 slash commands stored in `mycc/data/commands/`
- **Configs**: Configuration templates in `mycc/data/config/`
- **Access**: Uses `importlib.resources` for reliable data file access
- **Packaging**: Data files are included in the wheel/conda package
- **Test Mode**: Temporary directories via dependency injection instead of business logic penetration

## MCP Server Management

MCP (Model Context Protocol) servers provide enhanced capabilities:
- **context7**: Document analysis and context management

Installed via `claude mcp add` commands with user scope.

## Testing Architecture

MYCC uses a clean pytest-based testing approach with dependency injection:

### Test Structure
- **Unit Tests** (`tests/test_modules.py`): Fast, mocked component tests
- **Integration Tests** (`tests/test_integration.py`): Real CLI command tests  
- **Fixtures** (`tests/conftest.py`): Shared setup/teardown and environment management

### Test Mode Implementation
- **Environment Variable**: `MYCC_TEST_MODE=1` activates test mode
- **Dependency Injection**: Test paths injected into ModuleManager constructor
- **No Business Logic Penetration**: Test mode handled at CLI layer only
- **Automatic Cleanup**: Pytest fixtures handle directory cleanup

### Running Tests
```bash
# All tests
pixi run -e dev test

# Specific test types  
pixi run -e dev unit-test
pixi run -e dev integration-test

# With verbose output
pixi run -e dev pytest -v
```

## Packaging & Distribution

MYCC is distributed as conda packages with two variants:
- **Basic (`mycc`)**: Core functionality only
- **Full (`mycc-full`)**: Includes Node.js and npm dependencies

### Building Packages

Uses `pixi build` with rattler-build backend for modern, fast conda package creation:

```bash
# Build both variants using pixi build
pixi run -e build build

# Clean build artifacts
pixi run -e build clean-build
```

### Build System

- **Backend**: `pixi-build-rattler-build` for modern conda packaging
- **Versioning**: `hatch-vcs` automatically manages versions from git tags
- **Configuration**: `pixi.toml` with workspace preview features enabled

### Installation
```bash
# Install from conda-forge (when published)
pixi global install mycc

# Install from local build
pixi global install --channel conda-forge --channel ./output mycc
```

# important-instruction-reminders
- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary for achieving your goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
- Run any python command with `pixi run <command>`
- Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks