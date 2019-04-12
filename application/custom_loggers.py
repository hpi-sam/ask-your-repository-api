"""
Helpers for creating custom loggers.
"""

import logging


def setup_file_logger(name, filename, format='%(asctime)s %(message)s'):
    """Configures a custom logger that writes to a file and returns it"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
