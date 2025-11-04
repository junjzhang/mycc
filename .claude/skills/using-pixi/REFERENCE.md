# Pixi Configuration Reference

Comprehensive reference for `pixi.toml` configuration file structure.

## Table of Contents

- [Project Section](#project-section)
- [Dependencies](#dependencies)
- [PyPI Dependencies](#pypi-dependencies)
- [Features](#features)
- [Environments](#environments)
- [Tasks](#tasks)
- [System Requirements](#system-requirements)
- [Activation](#activation)
- [Target](#target)

---

## Project Section

Defines project metadata and global settings.

```toml
[project]
name = "my-project"                    # Required: project name
version = "0.1.0"                      # Optional: version
description = "Project description"    # Optional: description
authors = ["Name <email@example.com>"] # Optional: list of authors
channels = ["conda-forge", "pytorch"]  # Required: conda channels
platforms = ["linux-64", "osx-arm64"]  # Required: target platforms
license = "MIT"                        # Optional: license
license-file = "LICENSE"               # Optional: license file path
readme = "README.md"                   # Optional: readme file
homepage = "https://example.com"       # Optional: homepage URL
repository = "https://github.com/..."  # Optional: repo URL
documentation = "https://docs..."      # Optional: docs URL
```

### Channels

Order matters! Pixi searches channels in order listed.

**Common channels**:
- `conda-forge`: General Python packages
- `pytorch`: PyTorch and related
- `nvidia`: CUDA packages
- `rapidsai`: GPU data science
- `bioconda`: Bioinformatics

**Custom channels**:
```toml
channels = [
  "https://prefix.dev/my-channel",
  "conda-forge"
]
```

### Platforms

Supported platforms:
- `linux-64`: Linux x86_64
- `linux-aarch64`: Linux ARM64
- `osx-64`: macOS Intel
- `osx-arm64`: macOS Apple Silicon
- `win-64`: Windows x86_64

---

## Dependencies

Conda packages for the default environment.

```toml
[dependencies]
python = ">=3.10,<3.12"           # Version range
numpy = "*"                        # Any version
pytorch = "2.1.*"                  # Minor version lock
pandas = ">=2.0"                   # Minimum version
scikit-learn = "~=1.3.0"          # Compatible release
cuda = { version = "12.1", build = "h12345_0" }  # Specific build
```

### Version Specifiers

| Syntax | Meaning | Example |
|--------|---------|---------|
| `*` | Any version | `numpy = "*"` |
| `>=X.Y` | Minimum version | `python = ">=3.10"` |
| `<X.Y` | Maximum version | `numpy = "<2.0"` |
| `>=X,<Y` | Range | `python = ">=3.10,<3.12"` |
| `X.Y.*` | Lock minor version | `pytorch = "2.1.*"` |
| `~=X.Y.Z` | Compatible release | `pandas = "~=2.0.0"` |

### Build Specification

```toml
[dependencies]
package = { version = "1.0", build = "py310_0" }
```

---

## PyPI Dependencies

Python packages from PyPI (when not available in conda).

```toml
[pypi-dependencies]
transformers = ">=4.30"
my-package = "*"

# Editable local package
my-local-pkg = { path = "./packages/my-pkg", editable = true }

# From git
my-git-pkg = { git = "https://github.com/user/repo.git" }
my-git-pkg-branch = { git = "https://github.com/user/repo.git", branch = "main" }
my-git-pkg-tag = { git = "https://github.com/user/repo.git", tag = "v1.0.0" }
my-git-pkg-rev = { git = "https://github.com/user/repo.git", rev = "abc123" }

# From URL
my-wheel = { url = "https://example.com/package.whl" }

# With extras
my-pkg = { version = "*", extras = ["dev", "test"] }
```

### PyPI Version Syntax

Same as pip:
- `==X.Y.Z`: Exact version
- `>=X.Y.Z`: Minimum version
- `~=X.Y.Z`: Compatible release
- `>=X,<Y`: Version range

---

## Features

Reusable dependency groups that can be combined.

```toml
[feature.dev.dependencies]
pytest = ">=7.0"
ruff = "*"
pyright = "*"

[feature.dev.pypi-dependencies]
jupyter = "*"
ipython = "*"

[feature.dev.tasks]
test = "pytest tests/"
lint = "ruff check ."

[feature.cuda.dependencies]
pytorch-cuda = "12.1"
cuda-toolkit = "12.1"

[feature.cuda.activation.env]
CUDA_VISIBLE_DEVICES = "0,1,2,3"
```

Features can contain:
- `dependencies`: Conda packages
- `pypi-dependencies`: PyPI packages
- `tasks`: Feature-specific tasks
- `activation.env`: Environment variables
- `system-requirements`: System constraints

---

## Environments

Named combinations of features.

```toml
[environments]
default = { solve-group = "default" }
dev = { features = ["dev"], solve-group = "default" }
prod = { features = ["prod"], solve-group = "prod" }
gpu = ["cuda"]
dev-gpu = { features = ["dev", "cuda"], solve-group = "default" }
```

### Solve Groups

Environments in same solve-group share dependency resolution.

**Benefits**:
- Faster solving (reuses solutions)
- More consistent (same base dependencies)
- Less disk space (shared cache)

**When to separate**:
- Conflicting dependencies
- Different Python versions
- Isolated production environment

**Example**:
```toml
[environments]
# Dev and test share solutions
default = { solve-group = "dev-group" }
dev = { features = ["dev"], solve-group = "dev-group" }
test = { features = ["test"], solve-group = "dev-group" }

# Prod is isolated
prod = { features = ["prod"], solve-group = "prod-group" }
```

---

## Tasks

Predefined commands that can be run with `pixi run <task>`.

### Simple Task

```toml
[tasks]
test = "pytest tests/"
lint = "ruff check ."
```

### Task with Options

```toml
[tasks.train]
cmd = "python train.py"                    # Command to run
cwd = "scripts/"                           # Working directory
depends-on = ["install-deps"]              # Run these tasks first
inputs = ["src/**/*.py"]                   # Input files (for caching)
outputs = ["models/**/*"]                  # Output files (for caching)
env = { CUDA_VISIBLE_DEVICES = "0" }      # Environment variables
```

### Full Task Schema

```toml
[tasks.my-task]
cmd = "command to run"                     # Required: command
cwd = "relative/path"                      # Optional: working directory
depends-on = ["other-task", "another"]    # Optional: task dependencies
inputs = ["src/**/*.py", "data/*.csv"]    # Optional: input glob patterns
outputs = ["output/**/*", "result.txt"]   # Optional: output glob patterns

[tasks.my-task.env]
VAR1 = "value1"
VAR2 = "value2"
```

### Task Dependencies

Tasks can depend on other tasks:

```toml
[tasks]
clean = "rm -rf build/"
build = { cmd = "python setup.py build", depends-on = ["clean"] }
test = { cmd = "pytest", depends-on = ["build"] }
```

Running `pixi run test` will execute: clean → build → test

### Multi-line Commands

```toml
[tasks.train]
cmd = """
python train.py \
  --config config.yaml \
  --epochs 100 \
  --batch-size 32
"""
```

### Feature-Specific Tasks

```toml
[feature.dev.tasks]
test = "pytest tests/"
lint = "ruff check ."

[feature.prod.tasks]
deploy = "bash deploy.sh"
```

### Task Environment Variables

Available variables:
- `$PIXI_PROJECT_ROOT`: Absolute path to project root
- `$PIXI_ENVIRONMENT_NAME`: Current environment name
- `$PIXI_PROJECT_NAME`: Project name from pixi.toml
- `$PIXI_PROJECT_VERSION`: Project version
- Any variables from `[activation.env]`

---

## System Requirements

Specify system constraints.

```toml
[system-requirements]
linux = "5.10"              # Minimum kernel version
cuda = "12.1"               # CUDA version
libc = { family = "glibc", version = "2.28" }
```

### Available Requirements

- `linux`: Linux kernel version
- `cuda`: CUDA version
- `macos`: macOS version
- `libc`: C library (glibc or musl)
- `archspec`: CPU architecture

---

## Activation

Environment variables and scripts to run when environment is activated.

### Environment Variables

```toml
[activation.env]
CUDA_HOME = "/usr/local/cuda"
TORCH_CUDA_ARCH_LIST = "8.0;9.0"
PROJECT_ROOT = "$PIXI_PROJECT_ROOT"
DATA_PATH = "$HOME/data"
PYTHONPATH = "$PIXI_PROJECT_ROOT/src:$PYTHONPATH"
```

Variables are set when:
- Running `pixi run <cmd>`
- Inside `pixi shell`

### Activation Scripts

```toml
[activation.scripts]
env_setup.sh = """
#!/bin/bash
echo "Environment activated!"
export CUSTOM_VAR="value"
"""
```

Or reference external file:
```toml
[activation.scripts]
"scripts/setup.sh" = "scripts/setup.sh"
```

---

## Target

Platform-specific configuration.

```toml
[target.linux-64.dependencies]
nvidia-cuda-toolkit = "12.1"

[target.osx-arm64.dependencies]
tensorflow-macos = "2.13"

[target.win-64.dependencies]
pytorch-cuda = { version = "12.1", channel = "pytorch" }
```

Use when:
- Different packages per platform
- Platform-specific versions
- OS-specific configuration

---

## Complete Example

```toml
[project]
name = "ml-project"
version = "0.1.0"
channels = ["conda-forge", "pytorch", "nvidia"]
platforms = ["linux-64", "osx-arm64"]

[dependencies]
python = ">=3.10,<3.12"
pytorch = "2.1.*"
numpy = "*"
pandas = ">=2.0"

[pypi-dependencies]
transformers = ">=4.30"
wandb = "*"

[feature.dev.dependencies]
pytest = "*"
ruff = "*"
jupyter = "*"

[feature.dev.tasks]
test = "pytest tests/"
lint = "ruff check ."
format = "ruff format ."

[feature.cuda.dependencies]
pytorch-cuda = "12.1"
cuda-toolkit = "12.1"

[feature.cuda.activation.env]
CUDA_VISIBLE_DEVICES = "0,1,2,3"
CUDA_HOME = "/usr/local/cuda"

[environments]
default = { solve-group = "main" }
dev = { features = ["dev"], solve-group = "main" }
gpu = { features = ["cuda"], solve-group = "main" }
dev-gpu = { features = ["dev", "cuda"], solve-group = "main" }

[tasks]
train = { cmd = "python train.py", env = { EPOCHS = "100" } }
evaluate = "python eval.py"

[tasks.train-distributed]
cmd = "torchrun --nproc_per_node=8 train.py"
depends-on = ["validate-config"]
env = { MASTER_PORT = "29500" }

[tasks.validate-config]
cmd = "python validate_config.py"

[activation.env]
PROJECT_ROOT = "$PIXI_PROJECT_ROOT"
DATA_DIR = "$PROJECT_ROOT/data"
MODEL_DIR = "$PROJECT_ROOT/models"

[system-requirements]
cuda = "12.1"

[target.linux-64.dependencies]
nvidia-cuda-toolkit = "12.1"
```

---

## Tips & Tricks

### Keep Dependencies Organized

```toml
# Base ML dependencies
[dependencies]
python = ">=3.10"
pytorch = "2.1.*"
numpy = "*"

# Development tools
[feature.dev.dependencies]
pytest = "*"
ruff = "*"

# Optional features
[feature.cuda.dependencies]
pytorch-cuda = "12.1"

[feature.distributed.dependencies]
horovod = "*"
```

### Use Solve Groups Wisely

Same group = faster, shared dependencies:
```toml
[environments]
default = { solve-group = "dev" }
dev = { features = ["dev"], solve-group = "dev" }
```

Different groups = isolated:
```toml
[environments]
dev = { solve-group = "dev" }
prod = { solve-group = "prod" }
```

### Task Composition

```toml
[tasks]
clean = "rm -rf build/ dist/"
build = { cmd = "python -m build", depends-on = ["clean"] }
test = { cmd = "pytest", depends-on = ["build"] }
publish = { cmd = "twine upload dist/*", depends-on = ["test"] }
```

### Conditional Platform Configuration

```toml
# Linux: use CUDA
[target.linux-64.dependencies]
pytorch-cuda = "12.1"

# macOS: use CPU or Metal
[target.osx-arm64.dependencies]
pytorch = "2.1.*"
```

---

## Troubleshooting Configuration

### Validate pixi.toml

```bash
pixi install --dry-run  # Check for errors without installing
```

### Debug Dependency Resolution

```bash
pixi tree                # Show dependency tree
pixi list                # List installed packages
```

### Check Environment Setup

```bash
pixi info                # Project info
pixi project info        # Detailed project info
pixi environment list    # List environments
```

---

## External Resources

- Official Reference: https://pixi.sh/latest/reference/pixi_toml/
- Configuration Examples: https://pixi.sh/latest/examples/
- Community Examples: https://github.com/prefix-dev/pixi/tree/main/examples
