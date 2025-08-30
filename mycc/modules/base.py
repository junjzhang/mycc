"""Base class for MYCC modules."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseModule(ABC):
    """Base class for all MYCC modules."""

    def __init__(self, project_root: Path, target_root: Path, test_mode: bool = False):
        self.project_root = project_root
        self.target_root = target_root
        self.test_mode = test_mode

    @abstractmethod
    def install(self) -> bool:
        """Install the module."""
        pass

    @abstractmethod
    def uninstall(self) -> bool:
        """Uninstall the module."""
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if module is installed."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get module description."""
        pass

    @abstractmethod
    def get_install_path(self) -> Path:
        """Get the installation path."""
        pass
