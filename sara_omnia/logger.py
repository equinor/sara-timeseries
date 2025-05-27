from loguru import logger
import os
import sys


def setup_logger() -> None:
    """
    Configures Loguru logger based on the ENVIRONMENT environment variable.
    """

    environment = os.getenv("ENVIRONMENT", "production").lower()

    logger.remove()

    if environment == "development":
        logger.add(
            sys.stdout,
            level="DEBUG",
            format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        )
        print("Logger configured for development environment.")
    else:
        logger.add(
            sys.stdout,
            level="INFO",
            format="{time} | {level} | {message}",
        )
        logger.add(sys.stderr, level="ERROR", format="{time} | {level} | {message}")
        print("Logger configured for production environment.")
