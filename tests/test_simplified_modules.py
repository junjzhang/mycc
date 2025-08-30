"""Simplified tests for the new MYCC architecture."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mycc.config import MCP_SERVERS, CONFIG_MAPPINGS
from mycc.manager import ModuleManager
from mycc.modules.deps import DepsModule
from mycc.modules.claude_user_setting import ClaudeUserSettingModule


class TestDepsModule:
    """Test dependency checking module."""

    def test_initialization(self):
        """Test DepsModule initialization."""
        deps = DepsModule()

        assert deps.DEPENDENCIES is not None
        assert len(deps.DEPENDENCIES) >= 3  # claude_cli, nodejs, npm
        assert all(key in deps.DEPENDENCIES for key in ["claude_cli", "nodejs", "npm"])

    def test_check_dependency_success(self):
        """Test successful dependency check."""
        deps = DepsModule()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="v18.0.0\n")
            result = deps._check_dependency("nodejs")

            assert result["installed"] is True
            assert result["version"] == "18.0.0"

    def test_check_dependency_failure(self):
        """Test failed dependency check."""
        deps = DepsModule()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = deps._check_dependency("nodejs")

            assert result["installed"] is False
            assert result["version"] is None

    def test_install_reports_status(self):
        """Test that install() reports dependency status."""
        deps = DepsModule()

        with patch.object(deps, "_check_dependency") as mock_check:
            mock_check.return_value = {"installed": True, "version": "1.0.0"}

            # Should return True if all required deps are available
            result = deps.install()
            assert result is True

    def test_is_installed(self):
        """Test is_installed method."""
        deps = DepsModule()

        with patch.object(deps, "_check_dependency") as mock_check:
            # All required deps available
            mock_check.return_value = {"installed": True, "version": "1.0.0"}
            assert deps.is_installed() is True

            # Some required deps missing
            mock_check.return_value = {"installed": False, "version": None}
            assert deps.is_installed() is False

    def test_get_status(self):
        """Test get_status method."""
        deps = DepsModule()

        with patch.object(deps, "_check_dependency") as mock_check:
            mock_check.return_value = {"installed": True, "version": "1.0.0"}

            status = deps.get_status()
            assert isinstance(status, dict)
            assert len(status) == len(deps.DEPENDENCIES)

            for _, info in status.items():
                assert "installed" in info
                assert "version" in info
                assert "name" in info


class TestClaudeUserSettingModule:
    """Test Claude user settings module."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.claude_dir = self.temp_path / ".claude"
        self.home_dir = self.temp_path / "home"
        self.data_dir = self.temp_path / "data"

        # Create directories
        self.claude_dir.mkdir(parents=True)
        self.home_dir.mkdir(parents=True)
        self.data_dir.mkdir(parents=True)

        # Create test data
        self.setup_test_data()

    def teardown_method(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()

    def setup_test_data(self):
        """Create test data files."""
        # Create command files
        commands_dir = self.data_dir / "commands"
        commands_dir.mkdir(parents=True)

        for i in range(3):
            (commands_dir / f"test_command_{i}.md").write_text(f"# Test Command {i}")

        # Create config files
        config_dir = self.data_dir / "config"
        for _, config_info in CONFIG_MAPPINGS.items():
            config_file = config_dir / config_info["source"]
            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text('{"test": "config"}')

    def test_initialization(self):
        """Test ClaudeUserSettingModule initialization."""
        module = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        assert module.claude_dir == self.claude_dir
        assert module.home_dir == self.home_dir
        assert module.data_dir == self.data_dir
        assert module.commands_dir == self.claude_dir / "commands"

    def test_install_commands(self):
        """Test commands installation."""
        module = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        result = module._install_commands()
        assert result is True

        # Check that files were copied
        assert (self.claude_dir / "commands").exists()
        command_files = list((self.claude_dir / "commands").glob("*.md"))
        assert len(command_files) == 3

    def test_install_configs(self):
        """Test configs installation."""
        module = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        result = module._install_configs()
        assert result is True

        # Check that symlinks were created
        for config_key in CONFIG_MAPPINGS:
            if config_key == "claude_settings":
                # Relative to claude_dir which is not home
                continue
            from mycc.config import get_config_target_path

            target_path = get_config_target_path(config_key, self.home_dir)
            if target_path.exists() or target_path.is_symlink():
                # Some configs might be successfully linked
                if target_path.is_symlink():
                    assert target_path.resolve().exists()

    def test_install_mcp_no_claude_cli(self):
        """Test MCP installation when Claude CLI is not available."""
        module = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = module._install_mcp()
            assert result is False  # Should fail when CLI not available

    def test_install_with_sub_modules(self):
        """Test installation with specific sub-modules."""
        module = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        # Install only commands
        result = module.install(["commands"])
        assert result is True

        # Check that only commands were installed
        assert module._is_commands_installed() is True

    def test_get_status(self):
        """Test status reporting."""
        module = ClaudeUserSettingModule(self.claude_dir, self.home_dir, self.data_dir)

        status = module.get_status()
        assert isinstance(status, dict)
        assert "commands" in status
        assert "configs" in status
        assert "mcp" in status

        for sub_status in status.values():
            assert "installed" in sub_status
            assert "description" in sub_status


class TestModuleManager:
    """Test the simplified module manager."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.claude_dir = self.temp_path / ".claude"
        self.home_dir = self.temp_path / "home"
        self.data_dir = self.temp_path / "data"

    def teardown_method(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test ModuleManager initialization."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        assert manager.claude_dir == self.claude_dir
        assert manager.home_dir == self.home_dir
        assert manager.data_dir == self.data_dir

        # Check modules are initialized
        assert "deps" in manager.modules
        assert "claude_user_setting" in manager.modules
        assert isinstance(manager.deps, DepsModule)
        assert isinstance(manager.claude_user_setting, ClaudeUserSettingModule)

    def test_default_initialization(self):
        """Test ModuleManager with default paths."""
        manager = ModuleManager()

        # Should use default paths
        assert manager.claude_dir == Path.home() / ".claude"
        assert manager.home_dir == Path.home()
        assert manager.data_dir.exists()  # Should find package data

    def test_install_module(self):
        """Test module installation."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        with patch.object(manager.deps, "install") as mock_install:
            mock_install.return_value = True

            result = manager.install_module("deps")
            assert result is True
            mock_install.assert_called_once()

    def test_install_module_with_kwargs(self):
        """Test module installation with additional arguments."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        with patch.object(manager.claude_user_setting, "install") as mock_install:
            mock_install.return_value = True

            result = manager.install_module("claude_user_setting", sub_modules=["commands"])
            assert result is True
            mock_install.assert_called_once_with(["commands"])

    def test_unknown_module(self):
        """Test handling of unknown module."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        result = manager.install_module("unknown_module")
        assert result is False

    def test_install_all(self):
        """Test install all modules."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        with patch.object(manager, "install_module") as mock_install:
            mock_install.return_value = True

            result = manager.install_all()
            assert result is True
            assert mock_install.call_count == 2  # deps + claude_user_setting

    def test_get_module_status(self):
        """Test getting module status."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        with patch.object(manager.deps, "get_description") as mock_desc:
            mock_desc.return_value = "Test description"
            with patch.object(manager.deps, "is_installed") as mock_installed:
                mock_installed.return_value = True
                with patch.object(manager.deps, "get_install_path") as mock_path:
                    mock_path.return_value = Path("/test/path")

                    status = manager.get_module_status("deps")

                    assert status["name"] == "deps"
                    assert status["description"] == "Test description"
                    assert status["installed"] is True
                    assert status["install_path"] == "/test/path"

    def test_get_all_status(self):
        """Test getting all module status."""
        manager = ModuleManager(self.claude_dir, self.home_dir, self.data_dir)

        status = manager.get_all_status()
        assert isinstance(status, dict)
        assert "deps" in status
        assert "claude_user_setting" in status


class TestConfig:
    """Test static configuration."""

    def test_config_mappings(self):
        """Test CONFIG_MAPPINGS structure."""
        assert isinstance(CONFIG_MAPPINGS, dict)
        assert len(CONFIG_MAPPINGS) > 0

        for key, config in CONFIG_MAPPINGS.items():
            assert isinstance(key, str)
            assert "name" in config
            assert "source" in config
            assert "target" in config
            assert "relative_to_home" in config

    def test_mcp_servers(self):
        """Test MCP_SERVERS structure."""
        assert isinstance(MCP_SERVERS, dict)
        assert len(MCP_SERVERS) > 0

        for key, server in MCP_SERVERS.items():
            assert isinstance(key, str)
            assert "name" in server
            assert "package" in server

    def test_path_functions(self):
        """Test path helper functions."""
        from mycc.config import get_config_source_path, get_config_target_path

        data_dir = Path("/test/data")
        home_dir = Path("/test/home")

        # Test with existing config key
        config_key = list(CONFIG_MAPPINGS.keys())[0]

        source_path = get_config_source_path(config_key, data_dir)
        target_path = get_config_target_path(config_key, home_dir)

        assert isinstance(source_path, Path)
        assert isinstance(target_path, Path)

        # Test with invalid key
        with pytest.raises(ValueError):
            get_config_source_path("invalid_key", data_dir)


if __name__ == "__main__":
    pytest.main([__file__])
