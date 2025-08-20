import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str) -> logging.Logger:
    """Create a configured logger with console and rotating file handlers.

    Environment variables:
      LOG_LEVEL: DEBUG/INFO/WARNING/ERROR (default INFO)
      LOG_FILE: path to log file (default ./app.log)
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)
    if logger.handlers:
        # Already configured
        return logger

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file_path = os.getenv("LOG_FILE", os.path.abspath("./app.log"))
    try:
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=1_000_000, backupCount=3
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # If file handler fails (e.g., permissions), continue with console only
        pass

    return logger

