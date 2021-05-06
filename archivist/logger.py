"""
Set up logging
"""
import logging


# base logger from which all loggers are propagated
LOGGER = logging.getLogger()

LOGFMT = "%(asctime)s.%(msecs)03d|%(threadName)s|%(levelname)s|%(name)s|%(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def set_logger(level):
    """
    Setup logger
    Also used by unittests
    """
    LOGGER.setLevel(level)  # pragma: no cover
    if not LOGGER.hasHandlers():  # pragma: no cover
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                fmt=LOGFMT,
                datefmt=DATEFMT,
            )
        )
        LOGGER.addHandler(handler)
