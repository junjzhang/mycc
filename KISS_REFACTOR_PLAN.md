# MYCC KISS 原则重构计划

## 🎯 重构目标

将 MYCC 从过度工程化的 2959 行代码简化为 ~700 行的精简工具，专注于 Claude 用户设置管理的核心功能。

## 📊 当前问题分析

### 过度复杂的架构
- **5层抽象**: CLI → Manager → BaseModule → ConcreteModule → Core Utils
- **21个Python文件**: 为管理25个markdown文件和3个配置文件
- **过度设计**: 完整的异常体系、装饰器、上下文管理器用于简单的文件操作

### 核心问题
1. **抽象过度**: BaseModule为3个简单模块提供192行的抽象层
2. **Test Mode渗透**: 测试逻辑渗透到所有业务层
3. **配置过度复杂**: ConfigRegistry用284行管理3个文件映射
4. **依赖管理过重**: 302行代码检查和安装外部依赖
5. **错误处理过度**: 394行的utils.py处理简单的错误情况

## 🏗️ 新架构设计

### 简化后的结构
```
mycc/
├── cli.py                      # Pydantic + Tyro CLI (150行)
├── manager.py                  # 核心模块管理器 (200行)
├── modules/
│   ├── deps.py                 # 依赖管理 (100行)
│   └── claude_user_setting.py # Claude用户设置管理 (200行)
├── config.py                   # 静态配置映射 (50行)
└── data/                       # 保持现有结构
    ├── commands/               # 25个slash commands
    ├── config/                 # 配置文件模板
    └── mcp/                    # MCP服务器配置
```

### 模块定义

#### 1. deps 模块
**功能**: 外部依赖管理
- 检查和安装 Claude Code CLI
- 检查 Node.js 环境（MCP依赖）
- 其他必要的外部工具检查

#### 2. claude_user_setting 模块
**功能**: Claude 用户设置管理（可分开安装）
- **commands**: 25个 slash commands (.md 文件复制)
- **configs**: Claude 配置文件符号链接
- **mcp**: MCP 服务器配置和安装

## 🎛️ 新的CLI接口

### 基本命令
```bash
# 单模块安装
mycc install deps                                    # 安装依赖
mycc install claude_user_setting                    # 安装所有用户设置

# 子模块安装
mycc install claude_user_setting --sub commands     # 只安装commands
mycc install claude_user_setting --sub configs      # 只安装configs
mycc install claude_user_setting --sub mcp          # 只安装mcp

# 组合安装
mycc install deps,claude_user_setting               # 安装依赖和所有设置
mycc install --all                                  # 安装一切

# 状态检查
mycc status                                         # 显示所有模块状态
mycc status --module deps                           # 只显示依赖状态
mycc status --module claude_user_setting            # 只显示用户设置状态

# 其他操作
mycc uninstall <modules>                            # 卸载指定模块
mycc list                                           # 列出可用模块
```

### CLI实现 (Pydantic + Tyro)
```python
from enum import Enum
from pydantic import BaseModel, Field
import tyro

class ModuleType(str, Enum):
    deps = "deps"
    claude_user_setting = "claude_user_setting"

class ClaudeSubModule(str, Enum):
    commands = "commands"
    configs = "configs"
    mcp = "mcp"

class Install(BaseModel):
    modules: list[ModuleType] = Field(description="Modules to install")
    sub: list[ClaudeSubModule] | None = Field(default=None, description="Sub-modules for claude_user_setting")
    all: bool = Field(default=False, description="Install everything")
    
    def run(self):
        manager = ModuleManager()
        for module in self.modules:
            if module == ModuleType.claude_user_setting and self.sub:
                manager.install_claude_user_setting(self.sub)
            else:
                manager.install_module(module)

class Status(BaseModel):
    module: ModuleType | None = Field(default=None, description="Check specific module only")
    
    def run(self):
        manager = ModuleManager()
        if self.module:
            self._show_module_status(manager, self.module)
        else:
            self._show_all_status(manager)
    
    def _show_all_status(self, manager):
        print("MYCC Status")
        print("═══════════════════════════════════════")
        
        # 检查deps模块
        deps_ok = self._show_deps_status(manager)
        print()  # 空行分隔
        
        # 检查claude_user_setting模块
        settings_ok = self._show_claude_settings_status(manager)
        print()
        
        if deps_ok and settings_ok:
            print("Installation Status: All modules ready ✨")
        else:
            print("Installation Status: Some modules need attention ⚠️")
```

## 🔍 Status 命令详细设计

### 预期输出效果

#### 全部安装正常
```bash
$ mycc status

MYCC Status
═══════════════════════════════════════
✅ deps                External dependencies  
   ├── Claude CLI       ✅ v1.2.3 installed
   ├── Node.js          ✅ v18.17.0 installed
   └── npm              ✅ v9.8.1 installed

✅ claude_user_setting  Claude user settings
   ├── commands         ✅ 25 files installed → ~/.claude/commands/
   ├── configs          ✅ 3 configs linked → ~/.claude/, ~/.config/
   └── mcp             ✅ 1 server installed (context7)

Installation Status: All modules ready ✨
```

#### 部分安装/有问题
```bash
$ mycc status

MYCC Status
═══════════════════════════════════════
❌ deps                External dependencies  
   ├── Claude CLI       ❌ not found (run: mycc install deps)
   ├── Node.js          ✅ v18.17.0 installed  
   └── npm              ✅ v9.8.1 installed

⚠️  claude_user_setting  Claude user settings (partial)
   ├── commands         ✅ 25 files installed → ~/.claude/commands/
   ├── configs          ❌ not installed
   └── mcp             ❌ not installed

Installation Status: Some modules need attention ⚠️
Run 'mycc install deps' to fix dependency issues
Run 'mycc install claude_user_setting --sub configs,mcp' to complete user settings
```

#### 单模块检查
```bash
$ mycc status --module claude_user_setting

Claude User Setting Status
═══════════════════════════════════════
⚠️  claude_user_setting  Claude user settings (partial)
   ├── commands         ✅ 25 files installed
   │                       Path: ~/.claude/commands/
   │                       Files: make-pr.md, scaffold.md, implement.md, ...
   ├── configs          ❌ not installed
   │                       Missing links:
   │                       - ~/.claude/settings.json
   │                       - ~/.config/ccstatusline/settings.json  
   │                       - ~/.tweakcc/config.json
   └── mcp             ❌ not installed
                           Available servers: context7
                           Run: mycc install claude_user_setting --sub mcp
```

### 状态检查逻辑实现

```python
# manager.py 中的状态检查方法
class ModuleManager:
    def get_deps_status(self):
        """获取依赖模块详细状态"""
        return {
            'claude_cli': {
                'installed': self._check_command_exists('claude'),
                'version': self._get_command_version('claude --version'),
                'install_hint': 'npm install -g @anthropic-ai/claude-code'
            },
            'nodejs': {
                'installed': self._check_command_exists('node'), 
                'version': self._get_command_version('node --version'),
                'install_hint': 'Install from https://nodejs.org'
            },
            'npm': {
                'installed': self._check_command_exists('npm'),
                'version': self._get_command_version('npm --version'),
                'install_hint': 'Comes with Node.js'
            }
        }
    
    def get_claude_user_setting_status(self):
        """获取Claude用户设置详细状态"""
        return {
            'commands': {
                'installed': self._check_commands_installed(),
                'details': self._get_commands_details(),
                'files_count': self._count_installed_commands(),
                'path': str(self.claude_dir / "commands")
            },
            'configs': {
                'installed': self._check_all_configs_linked(),
                'details': self._get_configs_details(),
                'linked_configs': self._get_linked_configs(),
                'missing_configs': self._get_missing_configs()
            },
            'mcp': {
                'installed': self._check_mcp_installed(),
                'details': self._get_mcp_details(),
                'installed_servers': self._get_installed_mcp_servers(),
                'available_servers': self._get_available_mcp_servers()
            }
        }
    
    def _check_commands_installed(self) -> bool:
        """检查commands是否安装"""
        commands_dir = self.claude_dir / "commands"
        return commands_dir.exists() and len(list(commands_dir.glob("*.md"))) > 0
    
    def _check_all_configs_linked(self) -> bool:
        """检查所有配置是否都已链接"""
        from config import CONFIG_MAPPINGS
        for config_name, config_info in CONFIG_MAPPINGS.items():
            target_path = self._resolve_config_path(config_info['target'])
            if not target_path.is_symlink():
                return False
        return True
    
    def _get_missing_configs(self) -> list[str]:
        """获取缺失的配置文件列表"""
        missing = []
        from config import CONFIG_MAPPINGS
        for config_name, config_info in CONFIG_MAPPINGS.items():
            target_path = self._resolve_config_path(config_info['target'])
            if not target_path.is_symlink():
                missing.append(str(target_path))
        return missing
```

### Status命令的优势

1. **层次化显示**：按模块-子模块结构清晰展示
2. **详细信息**：显示版本、路径、文件数量等具体信息
3. **问题诊断**：明确指出缺失项和修复建议
4. **可操作指导**：提供具体的修复命令
5. **灵活检查**：支持全部检查或单模块检查
6. **美观输出**：使用emoji和格式化让信息易读

## 🔧 核心实现

### 1. 简化的模块管理器
```python
# manager.py
class ModuleManager:
    def __init__(self, claude_dir: Path = None, home_dir: Path = None):
        self.claude_dir = claude_dir or Path.home() / ".claude"
        self.home_dir = home_dir or Path.home()
        
        self.deps = DepsModule()
        self.claude_settings = ClaudeUserSettingModule(self.claude_dir, self.home_dir)
    
    def install_module(self, module_name: str):
        if module_name == "deps":
            return self.deps.install()
        elif module_name == "claude_user_setting":
            return self.claude_settings.install()
    
    def install_claude_user_setting(self, sub_modules: list[str]):
        return self.claude_settings.install(sub_modules)
```

### 2. 依赖模块
```python
# modules/deps.py
class DepsModule:
    def install(self) -> bool:
        """检查和安装必要依赖"""
        success = True
        success &= self._check_claude_cli()
        success &= self._check_nodejs()
        return success
    
    def _check_claude_cli(self) -> bool:
        """检查Claude CLI是否安装"""
        # 简单的命令存在检查，不自动安装
        
    def _check_nodejs(self) -> bool:
        """检查Node.js是否安装"""
        # MCP服务器需要Node.js
```

### 3. Claude用户设置模块
```python
# modules/claude_user_setting.py
class ClaudeUserSettingModule:
    def __init__(self, claude_dir: Path, home_dir: Path):
        self.claude_dir = claude_dir
        self.home_dir = home_dir
    
    def install(self, sub_modules: list[str] = None) -> bool:
        """安装Claude用户设置"""
        if not sub_modules:
            sub_modules = ['commands', 'configs', 'mcp']
        
        success = True
        for sub in sub_modules:
            if sub == 'commands':
                success &= self._install_commands()
            elif sub == 'configs':
                success &= self._install_configs()
            elif sub == 'mcp':
                success &= self._install_mcp()
        return success
    
    def _install_commands(self) -> bool:
        """复制slash commands到~/.claude/commands/"""
        # 简单的文件复制逻辑
        
    def _install_configs(self) -> bool:
        """创建配置文件符号链接"""
        # 使用静态配置映射
        
    def _install_mcp(self) -> bool:
        """安装MCP服务器"""
        # 调用外部claude mcp add命令
```

### 4. 静态配置
```python
# config.py
CONFIG_MAPPINGS = {
    'claude_settings': {
        'source': 'claude/settings.json',
        'target': '.claude/settings.json',
        'relative_to_home': True,
    },
    'ccstatusline_settings': {
        'source': 'ccstatusline/settings.json',
        'target': '.config/ccstatusline/settings.json',
        'relative_to_home': True,
    },
    'tweakcc_config': {
        'source': 'tweakcc/config.json',
        'target': '.tweakcc/config.json',
        'relative_to_home': True,
    }
}

MCP_SERVERS = {
    'context7': {
        'package': 'npx -y @upstash/context7-mcp',
        'description': 'Context7 MCP server for enhanced context management',
    }
}
```

## 🧪 测试策略重构

### Test Mode完全下沉
```python
# 核心逻辑不包含任何test_mode判断
class ClaudeUserSettingModule:
    def __init__(self, claude_dir: Path, home_dir: Path):
        # 路径由外部注入，不关心是否为测试
        self.claude_dir = claude_dir
        self.home_dir = home_dir
```

### 测试使用依赖注入
```python
# tests/test_claude_user_setting.py
def test_install_commands(tmp_path):
    # 测试负责创建临时环境
    test_claude = tmp_path / ".claude"
    test_home = tmp_path / "home"
    
    # 依赖注入方式
    module = ClaudeUserSettingModule(test_claude, test_home)
    
    # 执行和验证
    result = module.install(['commands'])
    assert result is True
    assert (test_claude / "commands").exists()
```

## 📊 预期效果

### 代码量对比
| 组件 | 当前行数 | 目标行数 | 减少 |
|-----|---------|---------|------|
| CLI | 254 | 150 | -41% |
| Manager | 150 | 200 | +33%* |
| Modules | 800+ | 300 | -63% |
| Core Utils | 400+ | 50 | -88% |
| **总计** | **2959** | **700** | **-76%** |

*Manager行数增加是因为吸收了部分原本分散的逻辑

### 架构简化
- **层次**: 5层 → 3层
- **文件数**: 21个 → 7个
- **抽象复杂度**: 大幅降低

### 功能保持
- ✅ 模块化安装功能完整保留
- ✅ 所有现有命令继续支持
- ✅ 数据文件管理不变
- ✅ 基本错误处理保留

## 🚀 实施计划

### 第一阶段：核心重构
1. **创建新的模块结构**
   - 实现 `modules/deps.py`
   - 实现 `modules/claude_user_setting.py`
   - 创建 `config.py` 静态配置

2. **重写管理器**
   - 简化 `manager.py`
   - 移除所有抽象层
   - 使用依赖注入设计

3. **重构CLI**
   - 重写 `cli.py` 使用新的命令结构
   - 保持向后兼容的命令接口
   - 移除所有test_mode参数

### 第二阶段：测试重构
4. **重写测试套件**
   - 测试使用依赖注入
   - 移除所有test_mode相关逻辑
   - 保持测试覆盖率

5. **验证功能**
   - 确保所有现有功能正常
   - 性能测试和稳定性验证

### 第三阶段：清理
6. **删除旧代码**
   - 移除 `modules/base.py`
   - 移除 `core/utils.py`、`core/exceptions.py`
   - 移除 `modules/config_registry.py`
   - 清理 `core/resources.py`

7. **文档更新**
   - 更新 README 和文档
   - 更新 CLAUDE.md

## 🔮 未来扩展性

### Repo级配置支持
```python
# 未来可添加
class RepoSettingModule:
    def install(self, repo_path: Path):
        """在指定repo中安装claude配置"""
        # 支持项目级的.claude/配置
```

### 插件系统
- 为不同类型的Claude工具提供标准化配置管理
- 支持用户自定义配置模板

## ✅ 成功标准

1. **代码量减少至700行以内**
2. **保持所有现有功能**
3. **测试通过率100%**
4. **启动性能提升50%**
5. **新手理解代码时间减少70%**

---

这个重构计划将把MYCC从一个过度工程化的工具简化为一个专注、高效的Claude配置管理器，同时为未来的扩展奠定坚实基础。