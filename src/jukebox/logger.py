import logging
import sys

from jukebox.config import LOG_LEVEL, LOG_FORMAT

_is_logging_configured: bool = False


def configure_logging() -> None:
    """Configures loggers for logging purposes"""

    if _is_logging_configured:
        return

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(stream=sys.stdout),  # console
        ],
        force=True,
    )
