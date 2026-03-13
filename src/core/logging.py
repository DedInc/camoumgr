import logging
import os
import pathlib
from datetime import datetime


def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO,
) -> logging.Logger:
    pathlib.Path(log_dir).mkdir(exist_ok=True, parents=True)

    log_filename = datetime.now().strftime("camoumgr_%Y%m%d.log")
    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger("camoumgr")
    logger.setLevel(log_level)

    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"camoumgr.{name}")
    return logging.getLogger("camoumgr")
