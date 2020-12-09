import logging

from workers import __NAME__


class Logger:
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger(__NAME__)
        self._logger.setLevel(level=logging.INFO)
        self._logger.addHandler(logging.StreamHandler())

    def info(self, message):
        self._logger.info(message)

    def critical(self, message):
        self._logger.critical(message)


logger = Logger()
