#!/usr/bin/env python3

import logging
from gxiba import config


def logger_setup(level=config.LOGGING_LEVEL, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    """
    Logging handler across whole proyect
    :param level: logging level, defaults to 10 (logging.DEBUG)
    :param log_format: log format, defaults to %(asctime)s - %(name)s - %(levelname)s - %(message)s
    :return: logging.Loger instance already setup for log handling
    """
    # Logger creation
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Logger Console Handler
    logger_console_handler = logging.StreamHandler()
    logger_console_handler.setLevel(level)

    # Logger Formatter
    logger_formatter = logging.Formatter(log_format)
    logger_console_handler.setFormatter(logger_formatter)

    logger.addHandler(logger_console_handler)
    return logger


