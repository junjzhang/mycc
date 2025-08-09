#!/bin/bash
# CCPlugins Installer for Mac/Linux

set -e
COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$COMMANDS_DIR"


# Download commands from GitHub
REPO_URL="https://github.com/junjzhang/mycc/main/commands"
COMMANDS=(
    "cleanproject.md"
    "commit.md"
    "contributing.md"
    "create-todos.md"
    "docs.md"
    "explain-like-senior.md"
    "find-todos.md"
    "fix-imports.md"
    "fix-todos.md"
    "format.md"
    "implement.md"
    "make-it-pretty.md"
    "predict-issues.md"
    "remove-comments.md"
    "review.md"
    "scaffold.md"
    "security-scan.md"
    "session-end.md"
    "session-start.md"
    "test.md"
    "todos-to-issues.md"
    "undo.md"
    "understand.md"
    "refactor.md"
)

# Check for existing commands
EXISTING=0
for cmd in "${COMMANDS[@]}"; do
    if [ -f "$COMMANDS_DIR/$cmd" ]; then
        ((EXISTING++))
    fi
done

if [ $EXISTING -gt 0 ]; then
    echo "[WARNING] Found $EXISTING existing commands"
    read -p "Overwrite existing commands? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[CANCELLED] Installation cancelled."
        echo "Tip: Use uninstall script first to remove old commands."
        exit 0
    fi
fi

echo "Downloading commands..."
for cmd in "${COMMANDS[@]}"; do
    curl -sSL "$REPO_URL/$cmd" -o "$COMMANDS_DIR/$cmd"
done
echo "CCPlugins installed to $COMMANDS_DIR"
echo "Type / in Claude Code to see available commands"