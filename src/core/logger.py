"""
Unified Logging Module for New_Flow_RL

Provides consistent logging across all modules.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Union
from datetime import datetime


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for terminal output"""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.GRAY,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        record.levelname = f"{color}{record.levelname}{Colors.RESET}"

        # Add color to module name
        record.name = f"{Colors.CYAN}{record.name}{Colors.RESET}"

        return super().format(record)


def setup_logger(
    name: str = "new_flow_rl",
    level: Union[str, int] = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    log_format: Optional[str] = None,
    use_color: bool = True
) -> logging.Logger:
    """
    Setup and configure a logger.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        log_format: Custom log format string
        use_color: Whether to use colored output (terminal only)

    Returns:
        Configured logger instance
    """
    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers = []

    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_color and sys.stdout.isatty():
        console_formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        console_formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (no color)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "new_flow_rl") -> logging.Logger:
    """
    Get a logger instance by name.

    If the logger doesn't exist, creates one with default settings.

    Args:
        name: Logger name (usually module name)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If no handlers, setup with defaults
    if not logger.handlers:
        return setup_logger(name)

    return logger


# Module-level logger for this file
logger = get_logger(__name__)


# Convenience functions for quick logging
def debug(msg: str, *args, **kwargs):
    """Log debug message"""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log info message"""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log warning message"""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log error message"""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log critical message"""
    get_logger().critical(msg, *args, **kwargs)


class LogContext:
    """
    Context manager for temporary log level changes.

    Usage:
        with LogContext(level="DEBUG"):
            # This block will log at DEBUG level
            logger.debug("This will be shown")
    """

    def __init__(self, level: Union[str, int] = "DEBUG", logger_name: str = "new_flow_rl"):
        self.logger = logging.getLogger(logger_name)
        self.new_level = level if isinstance(level, int) else getattr(logging, level.upper())
        self.old_level = self.logger.level

    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)
        return False


class Timer:
    """
    Context manager for timing code blocks.

    Usage:
        with Timer("LLM call"):
            response = llm.call(prompt)
        # Logs: "LLM call completed in 1.23s"
    """

    def __init__(self, name: str, logger_instance: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger_instance or get_logger()
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        if exc_type is not None:
            self.logger.error(f"{self.name} failed after {duration:.2f}s: {exc_val}")
        else:
            self.logger.info(f"{self.name} completed in {duration:.2f}s")

        return False

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
