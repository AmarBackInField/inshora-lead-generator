"""
Logging utility functions for the application.
"""

import logging

# Get the application logger
logger = logging.getLogger("telephony-agent")


def log_info(message: str):
    """Log an info message."""
    logger.info(message)


def log_error(message: str):
    """Log an error message."""
    logger.error(message)


def log_warning(message: str):
    """Log a warning message."""
    logger.warning(message)


def log_debug(message: str):
    """Log a debug message."""
    logger.debug(message)


def log_exception(message: str):
    """Log an exception with traceback."""
    logger.exception(message)

