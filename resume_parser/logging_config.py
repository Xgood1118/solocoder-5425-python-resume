import logging
import sys


def setup_logging(level: str = "INFO"):
    """配置日志"""
    logger = logging.getLogger()
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    for logger_name in ["uvicorn", "uvicorn.access", "fastapi"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.setLevel(level)
        if not uvicorn_logger.handlers:
            uvicorn_logger.addHandler(console_handler)
