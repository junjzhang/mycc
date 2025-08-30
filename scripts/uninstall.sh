#!/bin/bash
# MYCC - Modular Claude Code Configuration Manager Uninstaller

set -e

echo "MYCC Uninstaller"
echo "================"

# Check if MYCC is installed
if ! command -v pixi &> /dev/null; then
    echo "[INFO] Pixi not found. Checking for direct Python installation..."
    if ! python3 -m mycc --help &> /dev/null 2>&1; then
        echo "[INFO] MYCC is not installed."
        exit 0
    fi
else
    if [ ! -f "pixi.toml" ]; then
        echo "[INFO] MYCC pixi project not found."
        exit 0
    fi
fi

echo "[INFO] MYCC installation found."
echo ""

# Show current status
echo "Current installation status:"
if command -v pixi &> /dev/null && [ -f "pixi.toml" ]; then
    pixi run status 2>/dev/null || echo "  Unable to show status"
else
    python3 -m mycc status 2>/dev/null || echo "  Unable to show status"  
fi

echo ""
read -p "Remove all MYCC modules and configurations? (y/N): " -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "[CANCELLED] Uninstall cancelled."
    exit 0
fi

# Uninstall modules using MYCC itself
echo "[INFO] Uninstalling MYCC modules..."
if command -v pixi &> /dev/null && [ -f "pixi.toml" ]; then
    pixi run uninstall 2>/dev/null || echo "  Some modules may have already been removed"
else
    python3 -m mycc uninstall --all 2>/dev/null || echo "  Some modules may have already been removed"
fi

# Clean pixi environment
if command -v pixi &> /dev/null && [ -f "pixi.toml" ]; then
    echo "[INFO] Cleaning pixi environment..."
    rm -rf .pixi 2>/dev/null || echo "  Pixi environment already clean"
fi

# Remove Python package if installed via pip
echo "[INFO] Removing MYCC Python package..."
python3 -m pip uninstall mycc -y 2>/dev/null || echo "  Package was not installed via pip"

# Clean up any remaining symlinks
echo "[INFO] Cleaning up configuration links..."
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
STATUSLINE_SETTINGS="$HOME/.config/ccstatusline/settings.json"

if [ -L "$CLAUDE_SETTINGS" ]; then
    rm "$CLAUDE_SETTINGS"
    echo "  - Removed Claude settings link"
fi

if [ -L "$STATUSLINE_SETTINGS" ]; then
    rm "$STATUSLINE_SETTINGS"  
    echo "  - Removed ccstatusline settings link"
fi

# Ask about backups
if [ -f "$HOME/.claude/settings.json.backup" ] || [ -f "$HOME/.config/ccstatusline/settings.json.backup" ]; then
    echo ""
    read -p "Remove backup configuration files? (y/N): " -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        [ -f "$HOME/.claude/settings.json.backup" ] && rm "$HOME/.claude/settings.json.backup" && echo "  - Removed Claude settings backup"
        [ -f "$HOME/.config/ccstatusline/settings.json.backup" ] && rm "$HOME/.config/ccstatusline/settings.json.backup" && echo "  - Removed ccstatusline settings backup"
    fi
fi

echo ""
echo "[SUCCESS] MYCC has been uninstalled."
echo "Thanks for trying MYCC!"