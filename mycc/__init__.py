"""MYCC - A modular Claude Code configuration manager."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mycc")
except PackageNotFoundError:
    # Development mode fallback
    __version__ = "dev"

__author__ = "junjzhang"
