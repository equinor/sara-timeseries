import sys

from loguru import logger


def setup_logger() -> None:
    """
    Configures Loguru logger.
    """

    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD at HH:mm:ss zz}</green> | <level>{level}</level> | <level>{message}</level>",
    )
