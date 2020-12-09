import logging

from workers import __NAME__


class Logger:
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger(__NAME__)
        self._logger.setLevel(level=logging.INFO)

        formatter = logging.Formatter(f"%(asctime)s \t %(levelname)s > %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self._logger.addHandler(handler)

    def info(self, message):
        self._logger.info(message)

    def critical(self, message):
        self._logger.critical(message)

    def debug(self, message):
        self._logger.debug(message)


logger = Logger()
