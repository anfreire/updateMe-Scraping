import logging
from constants import PATHS
from base.abstract.singleton import SingletonMetaclass

class Logs(metaclass=SingletonMetaclass):
    def __init__(self) -> None:
        self.clean_logs()
        self.logger = logging.getLogger("updateMe")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler = logging.FileHandler(PATHS.LOGS)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def __del__(self) -> None:
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def clean_logs(self) -> None:
        open(PATHS.LOGS, "w").close()

    def add_exception(self, e: Exception) -> None:
        self.logger.error(e, exc_info=True)