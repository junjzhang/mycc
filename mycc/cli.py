#!/usr/bin/env python3
"""MYCC CLI - Main command line interface using tyro and pydantic."""

import sys
from enum import Enum
from pathlib import Path

import tyro
from pydantic import Field, BaseModel

from mycc import __version__
from mycc.core.logger import get_logger, set_test_mode
from mycc.core.manager import ConfigManager

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class ModuleType(str, Enum):
    """Available module types."""

    commands = "commands"
    configs = "configs"
    mcp = "mcp"


class Install(BaseModel):
    """Install Claude Code modules."""

    modules: list[ModuleType] | None = Field(
        default=None, description="Modules to install. If not specified, use --all"
    )
    all: bool = Field(default=False, description="Install all available modules")
    test_mode: bool = Field(default=False, description="Use test mode (safe for development)")
    test_dir: Path | None = Field(default=None, description="Test directory path (default: current directory)")
    skip_deps: bool = Field(default=False, description="Skip dependency installation checks")
    no_auto_deps: bool = Field(default=False, description="Don't automatically install missing dependencies")

    def run(self):
        # Set up logger with test mode
        logger = get_logger()
        if self.test_mode:
            set_test_mode(True)
            
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)

        if self.test_mode:
            logger.info("Using fake directories for safe testing")

        # Check dependencies before installation (unless skipped)
        if not self.skip_deps:
            deps_ok = manager.ensure_dependencies(auto_install=not self.no_auto_deps)
            if not deps_ok and not self.test_mode:
                logger.warning("Some dependencies are missing. Installation may not work correctly.")

        if self.all:
            modules = [ModuleType.commands, ModuleType.configs, ModuleType.mcp]
            logger.info("Installing all modules (commands, configs, mcp)...")
        elif self.modules:
            modules = self.modules
        else:
            logger.warning("No modules specified. Use --all to install everything.")
            return

        for module in modules:
            try:
                success = manager.install_module(module.value)
                logger.install_feedback(module.value, success)
            except Exception as e:
                logger.install_feedback(module.value, False, str(e))


class Uninstall(BaseModel):
    """Uninstall Claude Code modules."""

    modules: list[ModuleType] | None = Field(
        default=None, description="Modules to uninstall. If not specified, use --all"
    )
    all: bool = Field(default=False, description="Uninstall all modules")
    test_mode: bool = Field(default=False, description="Use test mode (safe for development)")
    test_dir: Path | None = Field(default=None, description="Test directory path (default: current directory)")

    def run(self):
        # Set up logger with test mode
        logger = get_logger()
        if self.test_mode:
            set_test_mode(True)
            
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)

        if self.test_mode:
            logger.info("Using fake directories for safe testing")

        if self.all:
            modules = [ModuleType.commands, ModuleType.configs, ModuleType.mcp]
            logger.warning("Uninstalling all modules (commands, configs, mcp)...")
        elif self.modules:
            modules = self.modules
        else:
            logger.warning("No modules specified. Use --all to uninstall everything.")
            return

        for module in modules:
            try:
                success = manager.uninstall_module(module.value)
                if success:
                    logger.success(f"Uninstalled {module.value} module")
                else:
                    logger.failure(f"Failed to uninstall {module.value} module")
            except Exception as e:
                logger.failure(f"Error uninstalling {module.value}: {e}")


class Link(BaseModel):
    """Link configuration files to Claude directories."""

    test_mode: bool = Field(default=False, description="Use test mode (safe for development)")
    test_dir: Path | None = Field(default=None, description="Test directory path (default: current directory)")

    def run(self):
        # Set up logger with test mode  
        logger = get_logger()
        if self.test_mode:
            set_test_mode(True)
            
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)

        if self.test_mode:
            logger.info("Using fake directories for safe testing")

        try:
            success = manager.link_configs()
            if success:
                logger.success("Configuration files linked successfully")
            else:
                logger.failure("Failed to link configuration files")
        except Exception as e:
            logger.failure(f"Error linking configs: {e}")


class Status(BaseModel):
    """Show installation status of modules."""

    test_mode: bool = Field(default=False, description="Use test mode (safe for development)")
    test_dir: Path | None = Field(default=None, description="Test directory path (default: current directory)")

    def run(self):
        # Set up logger with test mode
        logger = get_logger()
        if self.test_mode:
            set_test_mode(True)
            
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)

        if manager.test_mode:
            logger.info("Using fake directories")

        logger.section("MYCC Status")

        status_info = manager.get_status()

        for module, info in status_info.items():
            if info["installed"]:
                logger.success(f"{module:<12} {info['description']}")
                if "path" in info:
                    logger.info(f"  Path: {info['path']}")
            else:
                logger.failure(f"{module:<12} {info['description']}")


class List(BaseModel):
    """List available modules."""

    test_mode: bool = Field(default=False, description="Use test mode (safe for development)")
    test_dir: Path | None = Field(default=None, description="Test directory path (default: current directory)")

    def run(self):
        # Set up logger with test mode
        logger = get_logger()
        if self.test_mode:
            set_test_mode(True)
            
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)

        if self.test_mode:
            logger.info("Listing modules")

        logger.section("Available Modules")

        modules = manager.get_available_modules()

        for module, info in modules.items():
            logger.success(f"{module:<12} {info['description']}")
            if "files" in info:
                logger.info(f"  Files: {len(info['files'])} items")


class Version(BaseModel):
    """Show version information."""

    def run(self):
        logger = get_logger()
        logger.info(f"MYCC version {__version__}")


class Deps(BaseModel):
    """Check and manage dependencies."""

    test_mode: bool = Field(default=False, description="Use test mode (safe for development)")
    install: bool = Field(default=False, description="Install missing dependencies")

    def run(self):
        # Set up logger with test mode
        logger = get_logger()
        if self.test_mode:
            set_test_mode(True)
            
        manager = ConfigManager(PROJECT_ROOT, self.test_mode)

        if self.test_mode:
            logger.info("Checking dependencies in test mode")

        if self.install:
            success = manager.ensure_dependencies(auto_install=True)
            if success:
                logger.success("All dependencies are ready!")
            else:
                logger.failure("Some dependencies failed to install.")
                sys.exit(1)
        else:
            # Just check and report status
            manager.check_dependencies()


def main():
    """Main entry point."""
    try:
        args = tyro.cli(
            Install | Uninstall | Link | Status | List | Version | Deps,
            description="MYCC - A modular Claude Code configuration manager",
        )
        args.run()
    except KeyboardInterrupt:
        logger = get_logger()
        logger.warning("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger = get_logger()
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
