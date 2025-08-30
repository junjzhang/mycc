"""Unified logging system for MYCC with color support and user-friendly output."""

import os
import sys
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from contextlib import contextmanager

from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init()


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors and icons to log messages."""
    
    # Color mapping for different log levels
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }
    
    # Icon mapping for different log levels
    ICONS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }
    
    def __init__(self, use_colors: bool = True, use_icons: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_icons = use_icons
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and icons."""
        # Get color and icon for this level
        color = self.COLORS.get(record.levelno, Fore.WHITE) if self.use_colors else ""
        icon = self.ICONS.get(record.levelno, "") if self.use_icons else ""
        reset = Style.RESET_ALL if self.use_colors else ""
        
        # Build the message
        message = record.getMessage()
        
        # Add test mode prefix if present
        if hasattr(record, 'test_mode') and record.test_mode:
            test_prefix = f"{Fore.CYAN}[TEST MODE] " if self.use_colors else "[TEST MODE] "
            message = test_prefix + message + (Style.RESET_ALL if self.use_colors else "")
        
        # Format final message
        if self.use_colors or self.use_icons:
            prefix = f"{icon} " if icon else ""
            return f"{color}{prefix}{message}{reset}"
        else:
            return message


class ProgressFormatter(ColoredFormatter):
    """Specialized formatter for progress messages."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format progress record with percentage if available."""
        message = record.getMessage()
        
        # Add progress info if available
        if hasattr(record, 'current') and hasattr(record, 'total'):
            if record.total > 0:
                percentage = (record.current / record.total) * 100
                progress_info = f" ({record.current}/{record.total} - {percentage:.0f}%)"
                message += progress_info
        
        # Use parent formatter for colors and icons
        record.msg = message
        record.args = ()
        return super().format(record)


class MyccLogger:
    """Main logger class for MYCC with specialized methods."""
    
    def __init__(self, name: str = "mycc", level: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.test_mode = os.getenv("MYCC_TEST_MODE", "0") == "1"
        
        # Set log level
        if level is None:
            level = os.getenv("MYCC_LOG_LEVEL", "INFO" if not self.test_mode else "DEBUG")
        
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up console handler with appropriate formatting."""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Choose formatter based on environment
        use_colors = sys.stdout.isatty() and not os.getenv("NO_COLOR")
        use_icons = not os.getenv("MYCC_NO_ICONS")
        
        formatter = ColoredFormatter(use_colors=use_colors, use_icons=use_icons)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _log_with_context(self, level: int, message: str, **context: Any):
        """Log message with additional context."""
        # Create extra dict for context
        extra = {"test_mode": self.test_mode}
        extra.update(context)
        
        self.logger.log(level, message, extra=extra)
    
    # Standard logging methods
    def debug(self, message: str, **context: Any):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **context)
    
    def info(self, message: str, **context: Any):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **context)
    
    def warning(self, message: str, **context: Any):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **context)
    
    def error(self, message: str, **context: Any):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **context)
    
    def critical(self, message: str, **context: Any):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **context)
    
    # User-friendly specialized methods
    def success(self, message: str, **context: Any):
        """Log success message with green checkmark."""
        icon = f"{Fore.GREEN}✓ " if sys.stdout.isatty() else "✓ "
        colored_message = f"{icon}{message}{Style.RESET_ALL if sys.stdout.isatty() else ''}"
        self._log_with_context(logging.INFO, colored_message, **context)
    
    def failure(self, message: str, **context: Any):
        """Log failure message with red X."""
        icon = f"{Fore.RED}✗ " if sys.stdout.isatty() else "✗ "
        colored_message = f"{icon}{message}{Style.RESET_ALL if sys.stdout.isatty() else ''}"
        self._log_with_context(logging.ERROR, colored_message, **context)
    
    def progress(self, message: str, current: int = 0, total: int = 0, **context: Any):
        """Log progress message with optional progress info."""
        # Create progress handler if needed
        progress_handler = logging.StreamHandler(sys.stdout)
        progress_formatter = ProgressFormatter(
            use_colors=sys.stdout.isatty() and not os.getenv("NO_COLOR"),
            use_icons=not os.getenv("MYCC_NO_ICONS")
        )
        progress_handler.setFormatter(progress_formatter)
        
        # Create temporary logger for progress
        progress_logger = logging.getLogger(f"{self.logger.name}.progress")
        progress_logger.setLevel(self.logger.level)
        progress_logger.handlers = [progress_handler]
        
        # Log with progress context
        extra = {"test_mode": self.test_mode, "current": current, "total": total}
        extra.update(context)
        
        progress_logger.info(message, extra=extra)
    
    def operation(self, operation: str):
        """Context manager for logging operations."""
        return self._operation_context(operation)
    
    @contextmanager
    def _operation_context(self, operation: str):
        """Context manager for operation logging."""
        self.info(f"Starting {operation}...")
        try:
            yield
            self.success(f"Completed {operation}")
        except Exception as e:
            self.error(f"Failed {operation}: {e}")
            raise
    
    def section(self, title: str):
        """Log a section header."""
        if sys.stdout.isatty():
            separator = "=" * 40
            colored_title = f"{Fore.CYAN}{title}{Style.RESET_ALL}"
            self._log_with_context(logging.INFO, colored_title)
            self._log_with_context(logging.INFO, separator)
        else:
            self._log_with_context(logging.INFO, f"{title}")
            self._log_with_context(logging.INFO, "=" * 40)
    
    def install_feedback(self, module: str, success: bool, error: Optional[str] = None):
        """Specialized logging for module installation."""
        if success:
            self.success(f"Installed {module} module")
        else:
            self.failure(f"Failed to install {module} module")
            if error:
                self.error(f"Error details: {error}")
    
    def dependency_check(self, name: str, found: bool, required: bool = True):
        """Log dependency check results."""
        if found:
            self.success(f"{name} found")
        else:
            req_text = " (required)" if required else " (optional)"
            level = logging.ERROR if required else logging.WARNING
            icon = "✗" if required else "⚠️"
            color = Fore.RED if required else Fore.YELLOW
            
            if sys.stdout.isatty():
                message = f"{color}{icon} {name} not found{req_text}{Style.RESET_ALL}"
            else:
                message = f"{icon} {name} not found{req_text}"
            
            self._log_with_context(level, message)
    
    def set_test_mode(self, enabled: bool):
        """Enable or disable test mode."""
        self.test_mode = enabled
    
    def set_level(self, level: str):
        """Set logging level."""
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))


# Global logger instance
_default_logger: Optional[MyccLogger] = None


def get_logger(name: str = "mycc", level: Optional[str] = None) -> MyccLogger:
    """Get logger instance."""
    global _default_logger
    if _default_logger is None or name != "mycc":
        _default_logger = MyccLogger(name, level)
    return _default_logger


def set_log_level(level: str):
    """Set global log level."""
    logger = get_logger()
    logger.set_level(level)


def set_test_mode(enabled: bool):
    """Set global test mode."""
    logger = get_logger()
    logger.set_test_mode(enabled)


# Convenience functions for common operations
def info(message: str, **context: Any):
    """Log info message using default logger."""
    get_logger().info(message, **context)


def warning(message: str, **context: Any):
    """Log warning message using default logger."""
    get_logger().warning(message, **context)


def error(message: str, **context: Any):
    """Log error message using default logger."""
    get_logger().error(message, **context)


def success(message: str, **context: Any):
    """Log success message using default logger."""
    get_logger().success(message, **context)


def failure(message: str, **context: Any):
    """Log failure message using default logger."""
    get_logger().failure(message, **context)


def progress(message: str, current: int = 0, total: int = 0, **context: Any):
    """Log progress message using default logger."""
    get_logger().progress(message, current, total, **context)