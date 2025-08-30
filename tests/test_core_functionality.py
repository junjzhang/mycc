"""Core functionality tests for ConfigsModule and ConfigRegistry."""

import os
import sys
import json
import tempfile
from pathlib import Path

import pytest

# Add the mycc module to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mycc.modules.configs import ConfigsModule
from mycc.modules.config_registry import ConfigEntry, ConfigRegistry


class TestConfigRegistry:
    """Test core ConfigRegistry functionality."""
    
    def setup_method(self):
        """Reset singleton for each test."""
        ConfigRegistry.reset_singleton()
    
    def test_config_entry_creation(self):
        """Test basic ConfigEntry creation and path resolution."""
        entry = ConfigEntry(
            name="test_config",
            source_path="source/config.json",
            target_path="target/config.json",
            relative_to_home=True
        )
        
        assert entry.name == "test_config"
        assert entry.source_path == "source/config.json"
        assert entry.relative_to_home is True
        
        # Test path resolution
        home_dir = Path("/home/user")
        config_dir = Path("/config")
        target = entry.get_target_path(home_dir, config_dir)
        expected = home_dir / "target/config.json"
        assert target == expected
        
    def test_registry_basic_operations(self):
        """Test basic registry operations."""
        registry = ConfigRegistry()
        
        entry = ConfigEntry(
            name="test",
            source_path="src.json",
            target_path="target.json"
        )
        
        # Test adding without auto-loading (mark as loaded first)
        registry._loaded = True
        registry.add_entry(entry)
        
        # Check if our test entry was added
        retrieved = registry.get_entry("test")
        assert retrieved is not None
        assert retrieved.name == "test"
        
        # Verify the entry is in the registry
        assert registry.has_entry("test")
        
        # Test removal
        removed = registry.remove_entry("test")
        assert removed is True
        assert not registry.has_entry("test")
        
    def test_toml_loading(self):
        """Test loading configuration from TOML file."""
        toml_content = '''
        [configs.app1]
        source_path = "app1/config.json"
        target_path = ".config/app1/settings.json"
        relative_to_home = true
        description = "App1 configuration"
        
        [configs.app2]
        source_path = "app2/config.json"
        target_path = "app2.json"
        relative_to_config = true
        required = false
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)
            
        try:
            registry = ConfigRegistry()
            registry.load_from_toml(temp_path)
            
            entries = registry.get_all_entries()
            assert len(entries) == 2
            
            app1 = entries["app1"]
            assert app1.relative_to_home is True
            assert app1.description == "App1 configuration"
            assert app1.required is True  # default
            
            app2 = entries["app2"]
            assert app2.relative_to_config is True
            assert app2.required is False
            
        finally:
            temp_path.unlink()


class TestConfigsModule:
    """Test core ConfigsModule functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        self.project_root = self.temp_path / "project"
        self.claude_dir = self.temp_path / ".test_claude"
        self.home_dir = self.temp_path / ".test_home"
        
        self.project_root.mkdir(parents=True)
        self.claude_dir.mkdir(parents=True)
        self.home_dir.mkdir(parents=True)
        
        self.config_data_dir = self.project_root / "mycc" / "data" / "config"
        self.config_data_dir.mkdir(parents=True)
        
        self.create_test_config_files()
        os.environ["MYCC_TEST_MODE"] = "1"
        
    def teardown_method(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()
        if "MYCC_TEST_MODE" in os.environ:
            del os.environ["MYCC_TEST_MODE"]
            
    def create_test_config_files(self):
        """Create test configuration files."""
        # Create source config files
        configs = {
            "claude/settings.json": {"editor": "vscode", "theme": "dark"},
            "ccstatusline/settings.json": {"show_git": True, "show_time": False},
            "tweakcc/config.json": {"auto_save": True, "format_on_save": True}
        }
        
        for config_path, content in configs.items():
            config_file = self.config_data_dir / config_path
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(content, f, indent=2)
                
        # Create test registry.toml
        registry_content = """
        [configs.claude_settings]
        description = "Test Claude settings"
        source_path = "claude/settings.json"
        target_path = "settings.json"
        relative_to_config = true
        
        [configs.ccstatusline_settings]
        description = "Test ccstatusline settings"
        source_path = "ccstatusline/settings.json"
        target_path = ".config/ccstatusline/settings.json"
        relative_to_home = true
        
        [configs.tweakcc_config]
        description = "Test TweakCC config"
        source_path = "tweakcc/config.json"
        target_path = ".tweakcc/config.json"
        relative_to_home = true
        """
        
        registry_file = self.config_data_dir / "registry.toml"
        with open(registry_file, 'w') as f:
            f.write(registry_content)
            
    def create_configs_module(self):
        """Create a ConfigsModule instance for testing."""
        configs = ConfigsModule(
            project_root=self.project_root,
            target_root=self.claude_dir,
            test_mode=True,
            home_dir=self.home_dir
        )
        # Load the test registry
        registry_file = self.config_data_dir / "registry.toml"
        configs.registry.load_from_toml(registry_file)
        return configs
        
    def test_module_initialization(self):
        """Test ConfigsModule initialization."""
        configs = self.create_configs_module()
        
        assert configs.project_root == self.project_root
        assert configs.target_dir == self.claude_dir
        assert configs.home_dir == self.home_dir
        assert configs.test_mode is True
        assert configs.registry is not None
        
    def test_get_files(self):
        """Test configuration file listing."""
        configs = self.create_configs_module()
        files = configs.get_files()
        
        expected_files = [
            "claude/settings.json",
            "ccstatusline/settings.json", 
            "tweakcc/config.json"
        ]
        
        assert len(files) == 3
        for expected_file in expected_files:
            assert expected_file in files
            
    def test_installation_lifecycle(self):
        """Test complete installation and uninstallation lifecycle."""
        configs = self.create_configs_module()
        
        # Initially not installed
        assert configs.is_installed() is False
        
        # Install
        result = configs.install()
        assert result is True
        
        # Verify symlinks were created
        claude_settings = self.claude_dir / "settings.json"
        ccstatusline_settings = self.home_dir / ".config" / "ccstatusline" / "settings.json"
        tweakcc_config = self.home_dir / ".tweakcc" / "config.json"
        
        assert claude_settings.is_symlink()
        assert ccstatusline_settings.is_symlink()
        assert tweakcc_config.is_symlink()
        
        # Verify symlink targets - they should point to actual config files
        # The exact path may vary due to resource access, so just check they're valid symlinks
        claude_target = claude_settings.resolve()
        ccstatusline_target = ccstatusline_settings.resolve() 
        tweakcc_target = tweakcc_config.resolve()
        
        # Verify they point to actual files and are named correctly
        assert claude_target.exists() and claude_target.name == "settings.json"
        assert ccstatusline_target.exists() and ccstatusline_target.name == "settings.json"
        assert tweakcc_target.exists() and tweakcc_target.name == "config.json"
        
        # Now installed
        assert configs.is_installed() is True
        
        # Uninstall
        result = configs.uninstall()
        assert result is True
        
        # Verify symlinks were removed
        assert not claude_settings.exists()
        assert not ccstatusline_settings.exists()
        assert not tweakcc_config.exists()
        
        # No longer installed
        assert configs.is_installed() is False
        
    def test_backup_mechanism(self):
        """Test backup mechanism with existing files."""
        configs = self.create_configs_module()
        
        # Create existing file
        existing_file = self.claude_dir / "settings.json"
        existing_content = {"existing": "content"}
        with open(existing_file, 'w') as f:
            json.dump(existing_content, f)
            
        # Install (should create backup)
        result = configs.install()
        assert result is True
        
        # Verify backup was created
        backup_file = self.claude_dir / "settings.json.backup"
        assert backup_file.exists()
        
        # Verify backup content
        with open(backup_file, 'r') as f:
            backup_content = json.load(f)
        assert backup_content == existing_content
        
        # Verify symlink was created
        assert existing_file.is_symlink()
        
    def test_symlink_replacement(self):
        """Test replacing existing symlinks."""
        configs = self.create_configs_module()
        
        # Create dummy target for initial symlink
        dummy_target = self.temp_path / "dummy.json"
        dummy_target.write_text('{"dummy": "content"}')
        
        # Create existing symlink
        existing_symlink = self.claude_dir / "settings.json"
        existing_symlink.symlink_to(dummy_target)
        
        # Install (should replace symlink)
        result = configs.install()
        assert result is True
        
        # Verify symlink was replaced (no backup should be created)
        backup_file = existing_symlink.with_suffix(".json.backup")
        assert not backup_file.exists()
        
        # Verify new symlink points to correct target
        assert existing_symlink.is_symlink()
        target = existing_symlink.resolve()
        assert target.exists() and target.name == "settings.json"


class TestExtensibility:
    """Test the extensibility of the configuration system."""
    
    def test_dynamic_configuration_addition(self):
        """Test that new configurations can be added without code changes."""
        registry = ConfigRegistry()
        
        # Load existing configurations
        registry.load_from_toml()
        initial_count = len(registry.get_all_entries())
        
        # Add new configuration dynamically
        new_entry = ConfigEntry(
            name="new_app",
            source_path="new_app/config.json",
            target_path=".config/new_app/settings.json",
            relative_to_home=True,
            description="Dynamically added configuration"
        )
        
        registry.add_entry(new_entry)
        
        # Verify addition
        updated_entries = registry.get_all_entries()
        assert len(updated_entries) == initial_count + 1
        assert "new_app" in updated_entries
        
        retrieved = registry.get_entry("new_app")
        assert retrieved is not None
        assert retrieved.description == "Dynamically added configuration"


if __name__ == "__main__":
    pytest.main([__file__])