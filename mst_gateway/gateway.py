from logging import Logger
from .config import Config


class Gateway:
    def __init__(self, config: Config, logger: Logger):
        self._config = config
        self._logger = logger

    def run(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass
