"""Centralized logging configuration for questfoundry-cli"""

import logging
import sys
from typing import Optional


# Map string log levels to logging module levels
LOG_LEVELS = {
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "trace": logging.DEBUG,  # Python doesn't have trace, use debug
}


def setup_logging(log_level: str = "info") -> None:
    """Configure logging for the CLI and questfoundry-py library.

    Args:
        log_level: Log level as string ('error', 'warning', 'info', 'debug', 'trace')
    """
    # Normalize log level
    log_level = log_level.lower()
    if log_level not in LOG_LEVELS:
        log_level = "info"

    level = LOG_LEVELS[log_level]

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with formatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter - varies by log level
    if level == logging.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure questfoundry-py logging
    qf_logger = logging.getLogger("questfoundry")
    qf_logger.setLevel(level)

    # Configure logging for specific noisy third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING if level != logging.DEBUG else logging.INFO)

    # Log that logging is configured
    logger = logging.getLogger(__name__)
    if level == logging.DEBUG:
        logger.debug(f"Logging configured at {log_level.upper()} level")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
