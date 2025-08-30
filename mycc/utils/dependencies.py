"""
Dependency checker and installer for MYCC
"""

import subprocess
import shutil
import sys
from pathlib import Path
from typing import NamedTuple

from colorama import Fore, Style


class DependencyInfo(NamedTuple):
    """Information about a dependency"""
    name: str
    package: str
    check_command: str
    install_command: str
    required: bool = True


class DependencyChecker:
    """Check and install MYCC dependencies"""
    
    # Dependency definitions
    DEPENDENCIES = {
        'claude_code': DependencyInfo(
            name="Claude Code",
            package="@anthropic-ai/claude-code",
            check_command="claude --version",
            install_command="npm install -g @anthropic-ai/claude-code",
            required=True
        ),
        'ccstatusline': DependencyInfo(
            name="ccstatusline",
            package="ccstatusline",
            check_command="ccstatusline --version",
            install_command="npm install -g ccstatusline",
            required=False
        ),
        'tweakcc': DependencyInfo(
            name="TweakCC",
            package="tweakcc",
            check_command="tweakcc --version",
            install_command="npm install -g tweakcc",
            required=False
        )
    }
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
    
    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        if self.test_mode:
            # In test mode, simulate some commands exist/don't exist
            return command in ['node', 'npm']
        
        return shutil.which(command) is not None
    
    def check_npm_package(self, package: str) -> bool:
        """Check if an npm package is installed globally"""
        if self.test_mode:
            # In test mode, simulate package status
            return package in ["ccstatusline", "tweakcc"]  # Simulate some packages exist
        
        try:
            result = subprocess.run(
                ["npm", "list", "-g", package],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_node_npm(self) -> tuple[bool, str | None]:
        """Check if Node.js and npm are available"""
        if not self.check_command_exists("node"):
            return False, "Node.js not found. Please install Node.js first."
        
        if not self.check_command_exists("npm"):
            return False, "npm not found. Please install npm first."
        
        try:
            if self.test_mode:
                version = "v18.17.0 (test mode)"
            else:
                result = subprocess.run(
                    ["node", "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                version = result.stdout.strip()
            
            return True, version
        except subprocess.CalledProcessError:
            return False, "Failed to get Node.js version"
    
    def check_claude_code(self) -> bool:
        """Check if Claude Code is installed"""
        if self.test_mode:
            return False  # Simulate not installed
        
        return self.check_command_exists("claude")
    
    def check_ccstatusline(self) -> bool:
        """Check if ccstatusline is installed"""
        return self.check_npm_package("ccstatusline")
    
    def check_tweakcc(self) -> bool:
        """Check if TweakCC is installed"""
        return self.check_npm_package("tweakcc")
    
    def check_mcp_support(self) -> bool:
        """Check if Claude Code MCP commands are available"""
        if self.test_mode:
            return True  # Simulate MCP support in test mode
        
        if not self.check_command_exists("claude"):
            return False
        
        try:
            # Try to run claude mcp list to verify MCP support
            result = subprocess.run(
                ["claude", "mcp", "--help"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_npm_package(self, package: str, display_name: str) -> bool:
        """Install an npm package globally"""
        if self.test_mode:
            print(f"  {Fore.CYAN}[TEST MODE] Simulating installation of {display_name}...{Style.RESET_ALL}")
            return True
        
        try:
            print(f"  📥 Installing {display_name}...")
            result = subprocess.run(
                ["npm", "install", "-g", package],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"  {Fore.GREEN}✓ Successfully installed {display_name}{Style.RESET_ALL}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  {Fore.RED}❌ Failed to install {display_name}{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}Error: {e.stderr.strip() if e.stderr else 'Unknown error'}{Style.RESET_ALL}")
            
            # Provide manual installation guide
            print(f"  {Fore.CYAN}💡 Manual installation:{Style.RESET_ALL}")
            print(f"    npm install -g {package}")
            if "permission" in str(e).lower():
                print(f"  {Fore.YELLOW}⚠️  If you get permission errors, try:{Style.RESET_ALL}")
                print(f"    sudo npm install -g {package}")
            
            return False
        except FileNotFoundError:
            print(f"  {Fore.RED}❌ npm not found. Please install Node.js and npm first.{Style.RESET_ALL}")
            return False
    
    def check_all_dependencies(self) -> dict[str, bool]:
        """Check status of all dependencies"""
        print(f"{Fore.CYAN}🔍 Checking dependencies...{Style.RESET_ALL}")
        
        status = {}
        
        # Check Node.js/npm first
        node_ok, node_info = self.check_node_npm()
        if node_ok:
            print(f"  {Fore.GREEN}✓ Node.js found ({node_info}){Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}✗ {node_info}{Style.RESET_ALL}")
            return {"node": False}
        
        # Check individual dependencies
        for key, dep in self.DEPENDENCIES.items():
            if key == 'claude_code':
                is_installed = self.check_claude_code()
            elif key == 'ccstatusline':
                is_installed = self.check_ccstatusline()
            elif key == 'tweakcc':
                is_installed = self.check_tweakcc()
            else:
                is_installed = False
            
            status[key] = is_installed
            
            if is_installed:
                print(f"  {Fore.GREEN}✓ {dep.name} found{Style.RESET_ALL}")
            else:
                status_icon = "✗" if dep.required else "○"
                color = Fore.RED if dep.required else Fore.YELLOW
                req_text = "" if dep.required else " (optional)"
                print(f"  {color}{status_icon} {dep.name} not found{req_text}{Style.RESET_ALL}")
        
        return status
    
    def ask_install_permission(self, missing_deps: list[str]) -> bool:
        """Ask user permission to install missing dependencies"""
        if self.test_mode:
            print(f"{Fore.CYAN}[TEST MODE] Auto-approving dependency installation{Style.RESET_ALL}")
            return True
        
        print(f"\n{Fore.YELLOW}📦 Missing dependencies detected:{Style.RESET_ALL}")
        for dep_key in missing_deps:
            dep = self.DEPENDENCIES[dep_key]
            req_text = " (required)" if dep.required else " (optional)"
            print(f"  - {dep.name}{req_text}")
        
        while True:
            try:
                answer = input(f"\nWould you like to install missing dependencies? (Y/n): ").strip().lower()
                if answer in ['', 'y', 'yes']:
                    return True
                elif answer in ['n', 'no']:
                    return False
                else:
                    print("Please answer 'y' or 'n'")
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Fore.YELLOW}Installation cancelled by user{Style.RESET_ALL}")
                return False
    
    def install_missing_dependencies(self, missing_deps: list[str]) -> bool:
        """Install missing dependencies"""
        success = True
        
        for dep_key in missing_deps:
            dep = self.DEPENDENCIES[dep_key]
            
            print(f"\n{Fore.CYAN}📦 Installing {dep.name}...{Style.RESET_ALL}")
            
            if dep_key == 'claude_code':
                install_success = self.install_npm_package(dep.package, dep.name)
            elif dep_key == 'ccstatusline':
                install_success = self.install_npm_package(dep.package, dep.name)
            elif dep_key == 'tweakcc':
                install_success = self.install_npm_package(dep.package, dep.name)
            else:
                install_success = False
            
            if not install_success:
                if dep.required:
                    success = False
                    print(f"  {Fore.RED}❌ Failed to install required dependency: {dep.name}{Style.RESET_ALL}")
                else:
                    print(f"  {Fore.YELLOW}⚠️  Optional dependency {dep.name} failed to install{Style.RESET_ALL}")
        
        return success
    
    def check_and_install_all(self, auto_install: bool = True) -> bool:
        """Check all dependencies and optionally install missing ones"""
        # Check current status
        status = self.check_all_dependencies()
        
        # Check for Node.js failure
        if "node" in status and not status["node"]:
            print(f"\n{Fore.RED}❌ Node.js/npm is required but not found.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Please install Node.js from: https://nodejs.org/{Style.RESET_ALL}")
            return False
        
        # Find missing dependencies
        missing_required = [key for key, dep in self.DEPENDENCIES.items() 
                          if dep.required and not status.get(key, False)]
        missing_optional = [key for key, dep in self.DEPENDENCIES.items() 
                          if not dep.required and not status.get(key, False)]
        
        if not missing_required and not missing_optional:
            print(f"\n{Fore.GREEN}✅ All dependencies are already installed!{Style.RESET_ALL}")
            return True
        
        missing_deps = missing_required + missing_optional
        
        # Ask permission if auto_install is enabled
        if auto_install:
            if not self.ask_install_permission(missing_deps):
                if missing_required:
                    print(f"\n{Fore.RED}❌ Required dependencies are missing. MYCC may not work correctly.{Style.RESET_ALL}")
                    return False
                else:
                    print(f"\n{Fore.YELLOW}⚠️  Some optional features may not be available.{Style.RESET_ALL}")
                    return True
            
            # Install missing dependencies
            install_success = self.install_missing_dependencies(missing_deps)
            
            if install_success:
                print(f"\n{Fore.GREEN}✅ All dependencies installed successfully!{Style.RESET_ALL}")
                return True
            else:
                print(f"\n{Fore.RED}❌ Some dependencies failed to install.{Style.RESET_ALL}")
                return False
        else:
            # Just report missing dependencies
            if missing_required:
                print(f"\n{Fore.YELLOW}⚠️  Required dependencies are missing:{Style.RESET_ALL}")
                for dep_key in missing_required:
                    dep = self.DEPENDENCIES[dep_key]
                    print(f"  - {dep.name}: {dep.install_command}")
                return False
            
            return True