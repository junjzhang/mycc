#!/usr/bin/env python3
"""MYCC CLI - Simplified command line interface using tyro and pydantic."""

import sys
from typing import List, Optional

import tyro
from pydantic import Field, BaseModel

from mycc import __version__
from mycc.manager import ModuleManager
from mycc.module_spec import ModuleSpec
from mycc.test_environment import TestEnvironment


def create_module_manager() -> ModuleManager:
    """Create ModuleManager with unified test mode handling."""
    TestEnvironment.print_test_mode_info()
    claude_dir, home_dir = TestEnvironment.get_manager_paths()
    return ModuleManager(claude_dir, home_dir)


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

        # Parse all module specifications at CLI layer - no string parsing in lower layers
        module_specs = ModuleSpec.parse_multiple(self.modules)

        success = True
        for spec in module_specs:
            result = manager.install_module(spec.name, sub_modules=spec.sub_modules)
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

        # Parse all module specifications at CLI layer - consistent with install
        module_specs = ModuleSpec.parse_multiple(self.modules)

        success = True
        for spec in module_specs:
            result = manager.uninstall_module(spec.name, sub_modules=spec.sub_modules)
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
