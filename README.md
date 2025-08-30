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

### Commands Module
- **24 Claude Code slash commands** for enhanced development workflow
- Commands include: `/commit`, `/refactor`, `/test`, `/review`, `/docs`, and more
- Automatically installed to `~/.claude/commands/`

### Configs Module  
- **Claude Code settings**: Auto-prompts, code generation preferences, editor settings
- **ccstatusline settings**: Git status, file counts, project info display  
- **TweakCC settings**: Enhanced features, UI customization, shortcuts
- Smart symlinking with automatic backup of existing configs

### MCP Module
- **Context7**: Document analysis and context management
- **Playwright**: Browser automation and web interaction
- Managed through Claude Code's MCP system

## 📋 Commands

```bash
# Installation
mycc install --all                    # Install all modules
mycc install --modules commands       # Install commands only
mycc install --modules configs        # Install configs only
mycc install --modules mcp            # Install MCP servers only

# Management  
mycc link                              # Link config files
mycc status                            # Show installation status
mycc list                              # List available modules
mycc deps                              # Check dependencies
mycc version                           # Show version

# Removal
mycc uninstall --all                   # Remove all modules
mycc uninstall --modules commands     # Remove commands only
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
pixi run install          # Install all modules
pixi run status           # Show status  
pixi run deps             # Check dependencies
pixi run dev-test         # Safe test mode
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

```
mycc/
├── mycc/                         # Python package
│   ├── cli.py                   # CLI interface
│   ├── core/manager.py          # Core functionality
│   ├── modules/                 # Module handlers
│   └── data/                    # Packaged data (included in wheel)
│       ├── commands/            # Claude Code slash commands (.md)
│       └── config/              # Configuration templates (.json)
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
