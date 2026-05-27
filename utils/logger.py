"""Logging helper that writes rotating test logs to artifacts."""

import logging
import os
from logging.handlers import RotatingFileHandler

_WORKER = os.environ.get("PYTEST_XDIST_WORKER", "master")


def get_logger(name="framework"):
    """Return a configured logger instance for the framework.

    Args:
        name: Logger name.
    """
    log_dir = "artifacts/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"test-{_WORKER}.log")

    logger = logging.getLogger(f"{name}-{_WORKER}")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
