"""Logging helper that writes rotating test logs to artifacts."""

import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name="framework"):
    """Return a configured logger instance for the framework.

    Args:
        name: Logger name.
    """
    log_dir = "artifacts/logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = RotatingFileHandler(
            f"{log_dir}/test.log", maxBytes=5 * 1024 * 1024, backupCount=3
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
