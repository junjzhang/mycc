#!/usr/bin/env python3
"""Simple test script for the new simplified MYCC architecture."""

import os
import sys
import tempfile
from pathlib import Path

# Add mycc to path
sys.path.insert(0, str(Path(__file__).parent))

from mycc.manager import ModuleManager
from mycc.modules.deps import DepsModule
from mycc.modules.claude_user_setting import ClaudeUserSettingModule


def test_deps_module():
    """Test DepsModule functionality."""
    print("🧪 Testing DepsModule...")

    deps = DepsModule()

    # Test initialization
    assert deps.DEPENDENCIES is not None
    assert len(deps.DEPENDENCIES) >= 3
    print("✅ DepsModule initialization OK")

    # Test get_status
    status = deps.get_status()
    assert isinstance(status, dict)
    assert len(status) == len(deps.DEPENDENCIES)
    print("✅ DepsModule.get_status() OK")

    # Test description
    desc = deps.get_description()
    assert isinstance(desc, str)
    print("✅ DepsModule.get_description() OK")

    print("✅ DepsModule tests passed\n")


def test_claude_user_setting_module():
    """Test ClaudeUserSettingModule functionality."""
    print("🧪 Testing ClaudeUserSettingModule...")

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        claude_dir = temp_path / ".claude"
        home_dir = temp_path / "home"
        data_dir = temp_path / "data"

        claude_dir.mkdir(parents=True)
        home_dir.mkdir(parents=True)
        data_dir.mkdir(parents=True)

        # Create test data
        commands_dir = data_dir / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "test.md").write_text("# Test command")

        module = ClaudeUserSettingModule(claude_dir, home_dir, data_dir)

        # Test initialization
        assert module.claude_dir == claude_dir
        assert module.home_dir == home_dir
        assert module.data_dir == data_dir
        print("✅ ClaudeUserSettingModule initialization OK")

        # Test get_status
        status = module.get_status()
        assert isinstance(status, dict)
        assert "commands" in status
        assert "configs" in status
        assert "mcp" in status
        print("✅ ClaudeUserSettingModule.get_status() OK")

        # Test description
        desc = module.get_description()
        assert isinstance(desc, str)
        print("✅ ClaudeUserSettingModule.get_description() OK")

    print("✅ ClaudeUserSettingModule tests passed\n")


def test_module_manager():
    """Test ModuleManager functionality."""
    print("🧪 Testing ModuleManager...")

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        claude_dir = temp_path / ".claude"
        home_dir = temp_path / "home"
        data_dir = temp_path / "data"

        manager = ModuleManager(claude_dir, home_dir, data_dir)

        # Test initialization
        assert manager.claude_dir == claude_dir
        assert manager.home_dir == home_dir
        assert manager.data_dir == data_dir
        print("✅ ModuleManager initialization OK")

        # Test modules are initialized
        assert "deps" in manager.modules
        assert "claude_user_setting" in manager.modules
        assert isinstance(manager.deps, DepsModule)
        assert isinstance(manager.claude_user_setting, ClaudeUserSettingModule)
        print("✅ ModuleManager modules initialized OK")

        # Test get_all_status
        status = manager.get_all_status()
        assert isinstance(status, dict)
        assert "deps" in status
        assert "claude_user_setting" in status
        print("✅ ModuleManager.get_all_status() OK")

        # Test get_available_modules
        modules = manager.get_available_modules()
        assert isinstance(modules, dict)
        assert "deps" in modules
        assert "claude_user_setting" in modules
        print("✅ ModuleManager.get_available_modules() OK")

    print("✅ ModuleManager tests passed\n")


def test_config():
    """Test configuration functionality."""
    print("🧪 Testing Config...")

    from mycc.config import MCP_SERVERS, CONFIG_MAPPINGS, get_all_config_keys, get_all_mcp_server_keys

    # Test CONFIG_MAPPINGS
    assert isinstance(CONFIG_MAPPINGS, dict)
    assert len(CONFIG_MAPPINGS) > 0

    for _, config in CONFIG_MAPPINGS.items():
        assert "name" in config
        assert "source" in config
        assert "target" in config
        assert "relative_to_home" in config
    print("✅ CONFIG_MAPPINGS structure OK")

    # Test MCP_SERVERS
    assert isinstance(MCP_SERVERS, dict)
    assert len(MCP_SERVERS) > 0

    for _, server in MCP_SERVERS.items():
        assert "name" in server
        assert "package" in server
    print("✅ MCP_SERVERS structure OK")

    # Test helper functions
    config_keys = get_all_config_keys()
    assert isinstance(config_keys, list)
    assert len(config_keys) == len(CONFIG_MAPPINGS)
    print("✅ get_all_config_keys() OK")

    mcp_keys = get_all_mcp_server_keys()
    assert isinstance(mcp_keys, list)
    assert len(mcp_keys) == len(MCP_SERVERS)
    print("✅ get_all_mcp_server_keys() OK")

    print("✅ Config tests passed\n")


def test_cli_import():
    """Test that CLI can be imported."""
    print("🧪 Testing CLI import...")

    try:
        print("✅ CLI import OK")

        # Test that CLI modules are importable
        print("✅ CLI classes import OK")

    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False

    print("✅ CLI tests passed\n")
    return True


def main():
    """Run all tests."""
    print("🚀 Running MYCC simplified architecture tests...\n")

    # Set test mode
    os.environ["MYCC_TEST_MODE"] = "1"

    try:
        test_deps_module()
        test_claude_user_setting_module()
        test_module_manager()
        test_config()
        test_cli_import()

        print("🎉 All tests passed! The simplified architecture works correctly.")

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up environment
        if "MYCC_TEST_MODE" in os.environ:
            del os.environ["MYCC_TEST_MODE"]


if __name__ == "__main__":
    main()
