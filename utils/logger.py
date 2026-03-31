import logging
from logging.handlers import RotatingFileHandler
import os


def get_logger(name="framework"):
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
