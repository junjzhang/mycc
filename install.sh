#!/bin/bash
# CCPlugins Installer for Mac/Linux

set -e
COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$COMMANDS_DIR"


# Get list of commands from the commands directory
COMMANDS_SRC_DIR="$(cd "$(dirname "$0")" && pwd)/commands"
if [ ! -d "$COMMANDS_SRC_DIR" ]; then
    echo "[ERROR] 'commands' directory not found in $(cd "$(dirname "$0")" && pwd)."
    exit 1
fi

COMMANDS=()
while IFS= read -r -d $'\0' file; do
    COMMANDS+=("$(basename "$file")")
done < <(find "$COMMANDS_SRC_DIR" -name "*.md" -print0)


# Check for existing commands
EXISTING=0
for cmd in "${COMMANDS[@]}"; do
    if [ -f "$COMMANDS_DIR/$cmd" ]; then
        ((EXISTING++))
    fi
done

if [ $EXISTING -gt 0 ]; then
    echo "[WARNING] Found $EXISTING existing commands"
    read -p "Overwrite existing commands? (y/N): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[CANCELLED] Installation cancelled."
        echo "Tip: Use uninstall script first to remove old commands."
        exit 0
    fi
fi

echo "Installing commands from local directory..."
for cmd in "${COMMANDS[@]}"; do
    cp "$COMMANDS_SRC_DIR/$cmd" "$COMMANDS_DIR/$cmd"
done
echo "CCPlugins installed to $COMMANDS_DIR"
echo "Type / in Claude Code to see available commands"