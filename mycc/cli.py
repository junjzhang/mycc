#!/usr/bin/env python3
"""MYCC CLI - Main command line interface using tyro and pydantic."""

import sys
from enum import Enum
from pathlib import Path

import tyro
from colorama import Fore, Style, init
from pydantic import Field, BaseModel

from mycc import __version__
from mycc.core.manager import ConfigManager

# Initialize colorama for cross-platform colored output
init()

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
        default=None, 
        description="Modules to install. If not specified, use --all"
    )
    all: bool = Field(
        default=False, 
        description="Install all available modules"
    )
    test_mode: bool = Field(
        default=False,
        description="Use test mode (safe for development)"
    )
    test_dir: Path | None = Field(
        default=None,
        description="Test directory path (default: current directory)"
    )
    skip_deps: bool = Field(
        default=False,
        description="Skip dependency installation checks"
    )
    no_auto_deps: bool = Field(
        default=False,
        description="Don't automatically install missing dependencies"
    )

    def run(self):
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)
        
        if self.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Using fake directories for safe testing{Style.RESET_ALL}")
        
        # Check dependencies before installation (unless skipped)
        if not self.skip_deps:
            deps_ok = manager.ensure_dependencies(auto_install=not self.no_auto_deps)
            if not deps_ok and not self.test_mode:
                print(f"{Fore.YELLOW}⚠️  Some dependencies are missing. Installation may not work correctly.{Style.RESET_ALL}")
        
        if self.all:
            modules = [ModuleType.commands, ModuleType.configs]
            print(f"{Fore.GREEN}Installing all modules...{Style.RESET_ALL}")
        elif self.modules:
            modules = self.modules
        else:
            print(f"{Fore.YELLOW}No modules specified. Use --all to install everything.{Style.RESET_ALL}")
            return
        
        for module in modules:
            try:
                success = manager.install_module(module.value)
                if success:
                    print(f"{Fore.GREEN}✓ Installed {module.value} module{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Failed to install {module.value} module{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Error installing {module.value}: {e}{Style.RESET_ALL}")


class Uninstall(BaseModel):
    """Uninstall Claude Code modules."""

    modules: list[ModuleType] | None = Field(
        default=None, 
        description="Modules to uninstall. If not specified, use --all"
    )
    all: bool = Field(
        default=False, 
        description="Uninstall all modules"
    )
    test_mode: bool = Field(
        default=False,
        description="Use test mode (safe for development)"
    )
    test_dir: Path | None = Field(
        default=None,
        description="Test directory path (default: current directory)"
    )

    def run(self):
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)
        
        if self.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Using fake directories for safe testing{Style.RESET_ALL}")
        
        if self.all:
            modules = [ModuleType.commands, ModuleType.configs]
            print(f"{Fore.YELLOW}Uninstalling all modules...{Style.RESET_ALL}")
        elif self.modules:
            modules = self.modules
        else:
            print(f"{Fore.YELLOW}No modules specified. Use --all to uninstall everything.{Style.RESET_ALL}")
            return
        
        for module in modules:
            try:
                success = manager.uninstall_module(module.value)
                if success:
                    print(f"{Fore.GREEN}✓ Uninstalled {module.value} module{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Failed to uninstall {module.value} module{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Error uninstalling {module.value}: {e}{Style.RESET_ALL}")


class Link(BaseModel):
    """Link configuration files to Claude directories."""

    test_mode: bool = Field(
        default=False,
        description="Use test mode (safe for development)"
    )
    test_dir: Path | None = Field(
        default=None,
        description="Test directory path (default: current directory)"
    )
    
    def run(self):
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)
        
        if self.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Using fake directories for safe testing{Style.RESET_ALL}")
        
        try:
            success = manager.link_configs()
            if success:
                print(f"{Fore.GREEN}✓ Configuration files linked successfully{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Failed to link configuration files{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Error linking configs: {e}{Style.RESET_ALL}")


class Status(BaseModel):
    """Show installation status of modules."""

    test_mode: bool = Field(
        default=False,
        description="Use test mode (safe for development)"
    )
    test_dir: Path | None = Field(
        default=None,
        description="Test directory path (default: current directory)"
    )
    
    def run(self):
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)
        
        if manager.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Using fake directories{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}MYCC Status{Style.RESET_ALL}")
        print("=" * 40)
        
        status_info = manager.get_status()
        
        for module, info in status_info.items():
            status_icon = "✓" if info['installed'] else "✗"
            status_color = Fore.GREEN if info['installed'] else Fore.RED
            
            print(f"{status_color}{status_icon} {module:<12} {info['description']}{Style.RESET_ALL}")
            if info['installed'] and 'path' in info:
                print(f"  {'Path:':<10} {info['path']}")


class List(BaseModel):
    """List available modules."""

    test_mode: bool = Field(
        default=False,
        description="Use test mode (safe for development)"
    )
    test_dir: Path | None = Field(
        default=None,
        description="Test directory path (default: current directory)"
    )
    
    def run(self):
        manager = ConfigManager(PROJECT_ROOT, self.test_mode, self.test_dir)
        
        if self.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Listing modules{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Available Modules{Style.RESET_ALL}")
        print("=" * 40)
        
        modules = manager.get_available_modules()
        
        for module, info in modules.items():
            print(f"{Fore.GREEN}{module:<12}{Style.RESET_ALL} {info['description']}")
            if 'files' in info:
                print(f"  {'Files:':<10} {len(info['files'])} items")


class Version(BaseModel):
    """Show version information."""
    
    def run(self):
        print(f"MYCC version {__version__}")


class Deps(BaseModel):
    """Check and manage dependencies."""

    test_mode: bool = Field(
        default=False,
        description="Use test mode (safe for development)"
    )
    install: bool = Field(
        default=False,
        description="Install missing dependencies"
    )
    
    def run(self):
        manager = ConfigManager(PROJECT_ROOT, self.test_mode)
        
        if self.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Checking dependencies in test mode{Style.RESET_ALL}")
        
        if self.install:
            success = manager.ensure_dependencies(auto_install=True)
            if success:
                print(f"\n{Fore.GREEN}✅ All dependencies are ready!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}❌ Some dependencies failed to install.{Style.RESET_ALL}")
                sys.exit(1)
        else:
            # Just check and report status
            manager.check_dependencies()


def main():
    """Main entry point."""
    try:
        
        args = tyro.cli(
            Install
            | Uninstall 
            | Link
            | Status
            | List
            | Version
            | Deps,
            description="MYCC - A modular Claude Code configuration manager"
        )
        args.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()