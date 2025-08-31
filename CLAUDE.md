## Project Overview

MYCC is a modular Claude Code configuration manager built with Python 3.10+.

## Key features
Help user to install, uninstall preconfigured claude code setting and relative dependencies.
- Interactive CLI
  - `mycc install/uninstall` for install/uninstall setting / deps, support modular installation
  - `mycc status` for show installation status

## Architecture

**KISS 3-Layer Architecture:**
- **CLI** (`mycc/cli.py`): Simple Pydantic+Tyro interface with environment-based test mode
- **ModuleManager** (`mycc/manager.py`): Dependency injection-based module orchestrator
- **Modules**:
  - `deps`: responding for managing useful dependencies for claude code, like ccusage, ccstatusline, mcps, etc.
  - `claude_user_setting`: responding for managing pre-configured settings in `~/.claude`, currently includes commands/configs/mcp
- **Pre-configured setting**
  - `mycc/config.py`: Simple Python dictionaries for mcp and linking info
  - `mycc/data/config/`: Directory for configuration files, symbolically linked with automatic backup
  - `mycc/data/command`: Directory for slash command files

## Stack
- Pixi for dependency management
- Hatch-VCS for version control / packaging, rattler-build for building

## Code Style
- PEP 585 type hints

## Testing

MYCC uses a clean pytest-based testing approach with dependency injection:
- **Unit Tests** (`tests/test_modules.py`): Fast, mocked component tests
- **Integration Tests** (`tests/test_integration.py`): Real CLI command tests  
- **Fixtures** (`tests/conftest.py`): Shared setup/teardown and environment management
- **Environment Variable**: `MYCC_TEST_MODE=1` activates test mode

```bash
# All tests
pixi run -e dev test

# Specific test types  
pixi run -e dev unit-test
pixi run -e dev integration-test
```

## Building Packages

Uses `pixi build` with rattler-build backend for modern, fast conda package creation:

```bash
# Build both variants using pixi build
pixi run -e build build

# Clean build artifacts
pixi run -e build clean-build
```

# important-instruction-reminders
- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary for achieving your goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
- Run any python command with `pixi run <command>`
- Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks