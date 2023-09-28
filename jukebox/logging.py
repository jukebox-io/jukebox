import sys

from loguru import logger as _internal

from jukebox.globals import LOG_FORMAT, LOG_LEVEL

__all__ = ["Logger"]


class Logger:
    # logger configs
    log = _internal.log
    opt = _internal.opt

    trace = _internal.trace
    debug = _internal.debug
    info = _internal.info
    success = _internal.success
    warning = _internal.warning
    error = _internal.error
    critical = _internal.critical
    exception = _internal.exception

    _SETUP_COMPLETED: bool = False

    def __init__(self) -> None:
        raise NotImplementedError()

    @staticmethod
    def init_logger() -> None:
        """Configures loggers for logging purposes."""
        if Logger._SETUP_COMPLETED:
            return  # no-op

        # Remove any existing loggers
        _internal.remove()

        # Configure logging
        _internal.add(sys.stdout, level=LOG_LEVEL, format=LOG_FORMAT)

        Logger._SETUP_COMPLETED = True
