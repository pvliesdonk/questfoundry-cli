"""Centralized logging configuration for questfoundry-cli"""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI and questfoundry-py library.

    Args:
        verbose: If True, enable DEBUG level logging for all modules.
                If False, use INFO level.
    """
    # Set up root logger
    root_logger = logging.getLogger()

    # Determine log level based on verbose flag
    log_level = logging.DEBUG if verbose else logging.INFO
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with formatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    # Create formatter - simple format for INFO, detailed for DEBUG
    if verbose:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure questfoundry-py logging
    qf_logger = logging.getLogger("questfoundry")
    qf_logger.setLevel(log_level)

    # Configure logging for specific noisy third-party libraries (if needed)
    # These can be set to WARNING to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING if not verbose else logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
