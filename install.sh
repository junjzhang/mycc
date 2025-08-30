#!/bin/bash
# MYCC - Modular Claude Code Configuration Manager Installer

set -e

echo "MYCC - Modular Claude Code Configuration Manager"
echo "================================================"

# Check if pixi is available
if ! command -v pixi &> /dev/null; then
    echo "[ERROR] Pixi is required but not installed."
    echo "Please install pixi first:"
    echo "  curl -fsSL https://pixi.sh/install.sh | bash"
    echo "Then restart your shell and try again."
    exit 1
fi

echo "[INFO] Setting up pixi environment..."
pixi install

echo "[INFO] Installing MYCC modules..."
pixi run install

echo ""
echo "[SUCCESS] MYCC installed successfully!"
echo ""
echo "Usage (with pixi):"
echo "  pixi run install            # Install all modules"
echo "  pixi run install-commands   # Install commands only" 
echo "  pixi run install-configs    # Install configs only"
echo "  pixi run link-configs       # Link configuration files"
echo "  pixi run status             # Show installation status"
echo "  pixi run list               # List available modules"
echo ""
echo "Or directly:"
echo "  python -m mycc install --all"
echo "  python -m mycc status-command"
echo ""
echo "Quick start:"
echo "  pixi run install && pixi run link-configs"
echo ""
echo "Type 'pixi run --help' or 'python -m mycc --help' for more options."