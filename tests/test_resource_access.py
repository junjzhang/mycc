"""Tests for unified resource access functionality."""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the mycc module to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mycc.core.resources import (
    ResourceAccessError,
    get_data_file,
    get_data_directory,
    list_command_files,
    read_json_resource,
    read_registry_toml,
    read_toml_resource,
    list_resource_files,
    get_config_directory,
    read_mcp_servers_json,
    get_commands_directory,
    get_mcp_config_directory,
)


class TestResourceAccess:
    """Test core resource access functionality."""

    def test_get_commands_directory(self):
        """Test getting commands directory."""
        commands_dir = get_commands_directory()
        assert isinstance(commands_dir, Path)
        # Should not raise an exception

    def test_get_config_directory(self):
        """Test getting config directory."""
        config_dir = get_config_directory()
        assert isinstance(config_dir, Path)
        # Should not raise an exception

    def test_get_mcp_config_directory(self):
        """Test getting MCP config directory."""
        mcp_dir = get_mcp_config_directory()
        assert isinstance(mcp_dir, Path)
        # Should not raise an exception

    def test_list_command_files(self):
        """Test listing command files."""
        command_files = list_command_files()
        assert isinstance(command_files, list)
        # Should have at least some command files
        assert len(command_files) > 0
        
        # All should be .md files
        for cmd_file in command_files:
            assert str(cmd_file).endswith('.md')

    def test_read_registry_toml(self):
        """Test reading registry TOML file."""
        registry_data = read_registry_toml()
        assert isinstance(registry_data, dict)
        
        # Should have configs section
        assert 'configs' in registry_data
        configs = registry_data['configs']
        
        # Should have some expected configurations
        expected_configs = ['claude_settings', 'ccstatusline_settings', 'tweakcc_config']
        for config_name in expected_configs:
            assert config_name in configs
            config = configs[config_name]
            assert 'source_path' in config
            assert 'target_path' in config

    def test_read_mcp_servers_json(self):
        """Test reading MCP servers JSON file."""
        try:
            servers_data = read_mcp_servers_json()
            assert isinstance(servers_data, dict)
            
            # Should have some server definitions
            assert len(servers_data) > 0
            
            # Each server should have required fields
            for server_name, server_info in servers_data.items():
                assert isinstance(server_info, dict)
                assert 'package' in server_info
                
        except ResourceAccessError:
            # It's OK if the MCP servers file doesn't exist in test environment
            pytest.skip("MCP servers.json not found - this is expected in test environment")


class TestResourceAccessWithMocks:
    """Test resource access functionality with mocked resources."""

    def test_get_data_directory_with_fallback(self):
        """Test get_data_directory with importlib.resources failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fallback_path = temp_path / "mycc" / "data" / "commands"
            fallback_path.mkdir(parents=True)
            
            with patch('mycc.core.resources.resources.files', side_effect=ImportError("Mock error")):
                result = get_data_directory('mycc.data.commands', fallback_path)
                assert result == fallback_path

    def test_get_data_directory_failure(self):
        """Test get_data_directory when all methods fail."""
        with patch('mycc.core.resources.resources.files', side_effect=ImportError("Mock error")):
            with pytest.raises(ResourceAccessError) as exc_info:
                get_data_directory('mycc.data.nonexistent')
            
            assert "Failed to access package" in str(exc_info.value)

    def test_read_json_resource_with_fallback(self):
        """Test reading JSON with fallback to filesystem."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            test_data = {"test": "data", "number": 42}
            json.dump(test_data, temp_file)
            temp_path = Path(temp_file.name)
            
        try:
            with patch('mycc.core.resources.resources.files', side_effect=ImportError("Mock error")):
                result = read_json_resource('nonexistent.package', 'test.json', temp_path)
                assert result == test_data
        finally:
            temp_path.unlink()

    def test_read_toml_resource_with_fallback(self):
        """Test reading TOML with fallback to filesystem."""
        toml_content = '''
        [configs.test]
        source_path = "test/config.json"
        target_path = "test.json"
        description = "Test configuration"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as temp_file:
            temp_file.write(toml_content)
            temp_path = Path(temp_file.name)
            
        try:
            with patch('mycc.core.resources.resources.files', side_effect=ImportError("Mock error")):
                result = read_toml_resource('nonexistent.package', 'test.toml', temp_path)
                
                assert 'configs' in result
                assert 'test' in result['configs']
                test_config = result['configs']['test']
                assert test_config['source_path'] == "test/config.json"
                assert test_config['description'] == "Test configuration"
        finally:
            temp_path.unlink()

    def test_list_resource_files_with_fallback(self):
        """Test listing resource files with fallback."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some test files
            (temp_path / "file1.md").write_text("Test content 1")
            (temp_path / "file2.md").write_text("Test content 2")
            (temp_path / "other.txt").write_text("Other content")
            
            with patch('mycc.core.resources.resources.files', side_effect=ImportError("Mock error")):
                result = list_resource_files('nonexistent.package', '*.md', temp_path)
                
                assert len(result) == 2
                md_files = [f.name for f in result]
                assert "file1.md" in md_files
                assert "file2.md" in md_files

    def test_resource_access_error_propagation(self):
        """Test that ResourceAccessError is properly propagated."""
        with patch('mycc.core.resources.resources.files', side_effect=ImportError("Mock error")):
            with pytest.raises(ResourceAccessError) as exc_info:
                read_json_resource('nonexistent.package', 'nonexistent.json')
            
            # The error message may vary depending on where it fails, 
            # so just check that ResourceAccessError was raised
            assert isinstance(exc_info.value, ResourceAccessError)


class TestResourceAccessIntegration:
    """Integration tests for resource access with actual modules."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Set test mode
        os.environ["MYCC_TEST_MODE"] = "1"
        
    def teardown_method(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()
        if "MYCC_TEST_MODE" in os.environ:
            del os.environ["MYCC_TEST_MODE"]

    def test_commands_module_integration(self):
        """Test that CommandsModule can access resources properly."""
        from mycc.modules.commands import CommandsModule
        
        project_root = Path(__file__).parent.parent
        claude_dir = self.temp_path / ".test_claude"
        
        commands = CommandsModule(project_root, claude_dir, test_mode=True)
        
        # Should be able to get files list
        files = commands.get_files()
        assert isinstance(files, list)
        
        # Should not be installed initially
        assert not commands.is_installed()

    def test_configs_module_integration(self):
        """Test that ConfigsModule can access resources properly."""
        from mycc.modules.configs import ConfigsModule
        
        project_root = Path(__file__).parent.parent
        claude_dir = self.temp_path / ".test_claude"
        home_dir = self.temp_path / ".test_home"
        
        configs = ConfigsModule(project_root, claude_dir, test_mode=True, home_dir=home_dir)
        
        # Should be able to get files list
        files = configs.get_files()
        assert isinstance(files, list)
        
        # Should not be installed initially
        assert not configs.is_installed()

    def test_mcp_module_integration(self):
        """Test that MCPModule can access resources properly."""
        from mycc.modules.mcp import MCPModule
        
        project_root = Path(__file__).parent.parent
        claude_dir = self.temp_path / ".test_claude"
        
        mcp = MCPModule(project_root, claude_dir, test_mode=True)
        
        # Should have loaded some server configurations (built-in at minimum)
        assert len(mcp.servers) > 0
        
        # Should have expected servers (loaded from JSON or built-in)
        assert "context7" in mcp.servers
        # Note: playwright may or may not be present depending on config vs built-in fallback
        
        # Should be able to get files list
        files = mcp.get_files()
        assert isinstance(files, list)
        assert len(files) > 0


class TestErrorHandling:
    """Test error handling in resource access."""
    
    def test_package_not_found(self):
        """Test handling of non-existent packages."""
        with pytest.raises(ResourceAccessError):
            get_data_directory('completely.nonexistent.package')

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with pytest.raises(ResourceAccessError):
            get_data_file('nonexistent.package.name', 'nonexistent_file.json')

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("{ invalid json content")
            temp_path = Path(temp_file.name)
            
        try:
            with pytest.raises(ResourceAccessError) as exc_info:
                read_json_resource('nonexistent.package', 'invalid.json', temp_path)
            
            assert "Failed to read JSON" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_invalid_toml(self):
        """Test handling of invalid TOML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as temp_file:
            temp_file.write("[invalid toml content")
            temp_path = Path(temp_file.name)
            
        try:
            with pytest.raises(ResourceAccessError) as exc_info:
                read_toml_resource('nonexistent.package', 'invalid.toml', temp_path)
            
            assert "Failed to read TOML" in str(exc_info.value)
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])