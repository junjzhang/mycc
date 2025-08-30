# MYCC - Modular Claude Code Configuration Manager

A modern, modular configuration management system for Claude Code, built with Python, Tyro, and Pixi. MYCC allows you to easily install, manage, and configure Claude Code commands and settings.

## 🚀 Quick Start

### Option 1: Using Pixi (Recommended)

```bash
# Install Pixi if you haven't already
curl -fsSL https://pixi.sh/install.sh | bash

# Clone and install
git clone https://github.com/junjzhang/mycc.git
cd mycc
./install.sh

# Quick setup - install everything
pixi run install && pixi run link-configs
```

### Option 2: Direct Installation

```bash
curl -fsSL https://raw.githubusercontent.com/junjzhang/mycc/main/install.sh | bash
```

## 🎯 Usage

### Command Line Interface

MYCC provides a clean, type-safe CLI with the following commands:

```bash
# Show help
python -m mycc --help

# Install modules
python -m mycc install --all                    # Install all modules
python -m mycc install --modules commands       # Install commands only
python -m mycc install --modules configs        # Install configs only

# Dependency management
python -m mycc deps                              # Check dependencies
python -m mycc deps --install                    # Install missing dependencies

# Manage configurations  
python -m mycc link                              # Link config files

# Check status
python -m mycc status                            # Show installation status
python -m mycc list                              # List available modules

# Uninstall
python -m mycc uninstall --all                  # Remove all modules
```

### Pixi Tasks (Shortcuts)

If you're using Pixi, you can use these convenient shortcuts:

```bash
pixi run install          # Install all modules
pixi run install-commands # Install commands only
pixi run install-configs  # Install configs only
pixi run link-configs     # Link configuration files
pixi run status           # Show status
pixi run list             # List modules
pixi run uninstall        # Remove all modules

# Dependency Management
pixi run deps             # Check dependencies  
pixi run deps-install     # Install missing dependencies

# Development & Testing
pixi run dev-test         # Safe test mode (uses fake directories)
pixi run test-clean       # Clean test directories
```

## 📁 Project Structure

```
mycc/                          # Claude Configuration Manager
├── pyproject.toml            # Python project configuration
├── pixi.toml                 # Pixi project and tasks
├── mycc/                     # Python package
│   ├── cli.py               # Tyro-based CLI
│   ├── core/                # Core functionality
│   │   └── manager.py       # Configuration manager
│   └── modules/             # Module handlers
│       ├── commands.py      # Commands module
│       └── configs.py       # Configs module
├── commands/                # Command template files (24 commands)
├── config/                  # Configuration templates
│   ├── claude/              # Claude Code settings
│   └── ccstatusline/        # Status line settings
├── install.sh               # Installation script
└── uninstall.sh            # Uninstall script
```

## 🔧 Available Modules

### Commands Module
- **24 Claude Code slash commands** for enhanced development workflow
- Commands include: `/commit`, `/refactor`, `/test`, `/review`, `/docs`, and more
- Automatically installed to `~/.claude/commands/`

### Configs Module  
- **Claude Code settings**: Auto-prompts, code generation preferences, editor settings
- **CCStatusline settings**: Git status, file counts, project info display
- **TweakCC settings**: Enhanced features, UI customization, shortcuts, and integrations
- Smart symlinking with automatic backup of existing configs

### MCP Module
- **Context7**: Document analysis and context management with AI-powered indexing
- **Playwright**: Browser automation, web scraping, and interaction capabilities
- Managed through Claude Code's MCP system with user scope installation

## 🗑️ Uninstall

```bash
# Using the uninstall script
./uninstall.sh

# Or via curl
curl -fsSL https://raw.githubusercontent.com/junjzhang/mycc/main/uninstall.sh | bash
```

## 🧪 Development & Testing

MYCC includes a safe test mode for development that uses fake directories instead of your real `.claude` configuration:

```bash
# Test mode via CLI flags
python -m mycc install --all --test-mode
python -m mycc status --test-mode

# Test mode via environment variable
MYCC_TEST_MODE=1 python -m mycc status

# Comprehensive test suite
pixi run dev-test
```

All test operations use `.test_claude` and `.test_home` directories, keeping your real configuration safe.

## 🛠️ Dependency Management

MYCC automatically detects and can install required dependencies:

- **Claude Code**: The main CLI tool (`@anthropic-ai/claude-code`)
- **ccstatusline**: Status line enhancement (optional)
- **TweakCC**: Claude Code enhancement and customization tool (optional)
- **ccusage**: Usage analysis and monitoring tool (optional)

```bash
# Check what's installed
pixi run deps

# Install missing dependencies  
pixi run deps-install

# During module installation, dependencies are checked automatically
# Skip dependency checks with --skip-deps flag
python -m mycc install --all --skip-deps
```

## 🙏 Acknowledgments

Special thanks to:
- [brennercruvinel/CCPlugins](https://github.com/brennercruvinel/CCPlugins/tree/main/commands) for the foundation and inspiration for the commands
- The Claude Code community for making development more productive

## 📄 License

MIT License - feel free to use this project for your own Claude Code setup!