#!/usr/bin/env python3
"""MYCC CLI - Simplified command line interface using tyro and pydantic."""

import os
import sys
from typing import List, Optional
from pathlib import Path

import tyro
from pydantic import Field, BaseModel

from mycc import __version__
from mycc.manager import ModuleManager


def create_module_manager() -> ModuleManager:
    """Create ModuleManager with test mode handling."""
    test_mode = bool(os.getenv("MYCC_TEST_MODE", ""))

    if test_mode:
        claude_dir = Path.cwd() / ".test_claude"
        home_dir = Path.cwd() / ".test_home"
        print("🧪 Using test mode with temporary directories")
        # In test mode, use test directories but let data_dir default to real package data
        return ModuleManager(claude_dir, home_dir)
    else:
        return ModuleManager()


class Install(BaseModel):
    """Install Claude Code modules."""

    modules: Optional[List[str]] = Field(
        default=None, description="Modules to install: 'deps', 'commands', 'configs', 'mcp', or 'claude_user_setting'"
    )
    all: bool = Field(default=False, description="Install all available modules")
    skip_deps: bool = Field(default=False, description="Skip dependency checks")

    def run(self):
        manager = create_module_manager()

        # Install all modules
        if self.all:
            success = manager.install_all()
            if success:
                print("✅ All modules installed successfully")
            else:
                print("❌ Some modules failed to install")
                sys.exit(1)
            return

        # Install specific modules
        if not self.modules:
            print("❌ No modules specified. Use --all to install everything or specify modules.")
            print("Available modules: deps, claude_user_setting")
            print("Claude user setting sub-modules: commands, configs, mcp")
            return

        success = True
        for module_spec in self.modules:
            # Handle sub-module specifications like "claude_user_setting:commands,configs"
            if ":" in module_spec:
                module_name, sub_modules_str = module_spec.split(":", 1)
                sub_modules = [sm.strip() for sm in sub_modules_str.split(",")]
                result = manager.install_module(module_name, sub_modules=sub_modules)
            else:
                result = manager.install_module(module_spec)

            if not result:
                success = False

        if not success:
            sys.exit(1)


class Uninstall(BaseModel):
    """Uninstall Claude Code modules."""

    modules: Optional[List[str]] = Field(default=None, description="Modules to uninstall")
    all: bool = Field(default=False, description="Uninstall all modules")

    def run(self):
        manager = create_module_manager()

        # Uninstall all modules
        if self.all:
            success = True
            for module_name in ["deps", "claude_user_setting"]:
                if not manager.uninstall_module(module_name):
                    success = False

            if success:
                print("✅ All modules uninstalled successfully")
            else:
                print("❌ Some modules failed to uninstall")
                sys.exit(1)
            return

        # Uninstall specific modules
        if not self.modules:
            print("❌ No modules specified. Use --all to uninstall everything.")
            return

        success = True
        for module_spec in self.modules:
            # Handle sub-module specifications
            if ":" in module_spec:
                module_name, sub_modules_str = module_spec.split(":", 1)
                sub_modules = [sm.strip() for sm in sub_modules_str.split(",")]
                result = manager.uninstall_module(module_name, sub_modules=sub_modules)
            else:
                result = manager.uninstall_module(module_spec)

            if not result:
                success = False

        if not success:
            sys.exit(1)


class Status(BaseModel):
    """Show installation status of modules."""

    module: Optional[str] = Field(default=None, description="Show status for specific module")

    def run(self):
        manager = create_module_manager()

        # Show status for specific module or all modules
        manager.show_status(self.module)


class List(BaseModel):
    """List available modules."""

    def run(self):
        manager = create_module_manager()

        # List all available modules
        manager.list_modules()


class Version(BaseModel):
    """Show version information."""

    def run(self):
        print(f"MYCC version {__version__}")


class Deps(BaseModel):
    """Check dependencies."""

    def run(self):
        manager = create_module_manager()

        # Just install deps module which checks dependencies
        success = manager.install_module("deps")
        if not success:
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        args = tyro.cli(
            Install | Uninstall | Status | List | Version | Deps,
            description="MYCC - A modular Claude Code configuration manager",
        )
        args.run()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
