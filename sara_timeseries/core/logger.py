from logging.config import dictConfig

from sara_timeseries.core.settings import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s - %(asctime)s - %(name)s -  %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": settings.LIB_LOG_LEVEL,
    },
    "loggers": {},
}


def setup_logger() -> None:
    dictConfig(LOGGING_CONFIG)
