"""Package logger configuration for flxtrd."""

import logging

# Create logger
LOGGER_NAME = "flxtrd"
flexLogger = logging.getLogger(LOGGER_NAME)
flexLogger.setLevel(logging.INFO)

DEFAULT_FORMATTER = logging.Formatter(
    "%(levelname)s %(name)s %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
)

# Configure console logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(DEFAULT_FORMATTER)
flexLogger.addHandler(console_handler)

logger = logging.getLogger(LOGGER_NAME)
# main logger object
log = logger.log
