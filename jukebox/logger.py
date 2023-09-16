import logging
import sys

from jukebox.globals import LOG_LEVEL, LOG_FORMAT


_is_logging_configured: bool = False


def setup_loggers() -> None:
    """Configures loggers for logging purposes"""
    global _is_logging_configured

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
    _is_logging_configured = True
