# MYCC - Modular Claude Code Configuration Manager

A modern, modular configuration management system for Claude Code. MYCC allows you to easily install, manage, and configure Claude Code commands and settings.

## 🚀 Quick Start

### Package Installation (Recommended)

Install MYCC globally using pixi:

```bash
# Install the basic version (most users)
pixi global install --channel conda-forge mycc

# Or install from local build (for developers)
pixi global install --channel conda-forge --channel ./output mycc

# Verify installation
mycc --help
mycc version
```

### Basic Usage

```bash
# Install all modules (commands, configs, MCP servers)
mycc install --all

# Check installation status
mycc status

# Link configuration files (reuses configs module)
mycc link

# Show available modules
mycc list
```

## 🎯 Available Modules

MYCC uses a simplified modular architecture with two main module types:

### Dependencies Module (`deps`)
- **Automatic dependency detection**: Checks for Claude Code, ccstatusline, TweakCC, and ccusage
- **Optional installation**: Can install missing dependencies automatically
- **Status reporting**: Shows which tools are available

### Claude User Settings Module (`claude_user_setting`)
- **Commands sub-module**: 25+ slash commands (`.md` files) installed to `~/.claude/commands/`
- **Configs sub-module**: Configuration templates with smart symlinking and automatic backup
  - Claude Code settings (auto-prompts, preferences)
  - ccstatusline settings (git status, file counts) 
  - TweakCC settings (UI customization, shortcuts)
- **MCP sub-module**: Model Context Protocol servers
  - Context7: Document analysis and context management
  - Managed through Claude Code's MCP system

## 📋 Commands

```bash
# Installation
mycc install --all                              # Install all modules
mycc install --modules deps                     # Install dependencies module
mycc install --modules claude_user_setting      # Install all Claude user settings
mycc install --modules claude_user_setting:commands  # Commands only
mycc install --modules claude_user_setting:configs   # Configs only
mycc install --modules claude_user_setting:mcp       # MCP servers only

# Management  
mycc link                              # Link config files
mycc status                            # Show installation status
mycc list                              # List available modules
mycc deps                              # Check dependencies
mycc version                           # Show version

# Removal
mycc uninstall --all                           # Remove all modules
mycc uninstall --modules deps                  # Remove dependencies module
mycc uninstall --modules claude_user_setting   # Remove all Claude user settings
```

## 🛠️ Dependencies

MYCC automatically detects and can install required dependencies:

- **Claude Code**: The main CLI tool (`@anthropic-ai/claude-code`)
- **ccstatusline**: Status line enhancement
- **TweakCC**: Claude Code customization tool  
- **ccusage**: Usage analysis and monitoring

```bash
# Check dependencies
mycc deps

# Install missing dependencies automatically
mycc deps --install
```

## 🧪 Development Setup

For developers who want to contribute or customize:

```bash
# Clone the repository
git clone https://github.com/junjzhang/mycc.git
cd mycc

# Install pixi if needed
curl -fsSL https://pixi.sh/install.sh | bash

# Install in development mode
pixi run dev-install

# Run tests safely (uses fake directories)
pixi run dev-test
```

### Development Commands

```bash
pixi run install          # Install all modules in development mode
pixi run status           # Show status  
pixi run deps             # Check dependencies
pixi run test             # Run all tests (unit + integration)
pixi run integration-test # Run CLI integration tests
pixi run unit-test        # Run unit tests only
pixi run lint             # Code linting
pixi run format           # Code formatting
```

## 🏗️ Building Packages

```bash
# Build packages
pixi run -e build build

# Upload to conda repository
pixi run upload
```

## 📁 Project Structure

MYCC uses a simplified 3-layer architecture after KISS refactoring:

```
mycc/
├── mycc/                         # Python package
│   ├── cli.py                   # CLI interface (Tyro+Pydantic)
│   ├── manager.py               # Module manager (core orchestrator)
│   ├── config.py                # Configuration management
│   ├── modules/                 # Module implementations
│   │   ├── deps.py              # Dependencies module
│   │   └── claude_user_setting.py  # Claude user settings module
│   └── data/                    # Packaged data (included in wheel)
│       ├── commands/            # Claude Code slash commands (.md)
│       └── config/              # Configuration templates (.json)
├── tests/                       # Pytest test suite
│   ├── conftest.py              # Shared fixtures
│   ├── test_integration.py      # CLI integration tests
│   └── test_modules.py          # Unit tests
└── scripts/                     # Build and deployment
```

## 🗑️ Uninstall

```bash
# Remove MYCC modules
mycc uninstall --all

# Remove the package itself
pixi global remove mycc
```

## 🙏 Acknowledgments

Special thanks to:
- [brennercruvinel/CCPlugins](https://github.com/brennercruvinel/CCPlugins/tree/main/commands) for the foundation and inspiration for the commands
- The Claude Code community for making development more productive

## 📄 License

MIT License - feel free to use this project for your own Claude Code setup!
