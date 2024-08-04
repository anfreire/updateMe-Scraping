import logging
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Log:
    def __init__(self, log_file: str, debug: bool = False):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

        formatter = logging.Formatter(
            "\n[ %(levelname)s ] [ %(asctime)s ]\n%(message)s",
            datefmt="%m/%d/%Y - %H:%M:%S",
        )

        file_handler = logging.FileHandler(self.log_file, mode="w")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.clean()

    def clean(self):
        with open(self.log_file, "w"):
            pass

    def log(
        self, message: str, level: LogLevel = LogLevel.INFO, exception: bool = False
    ):
        level = level.value if isinstance(level, LogLevel) else level
        log_method = getattr(self.logger, level.lower())
        log_method(message, exc_info=exception)
        print(f"[ {level} ]\n{message}\n")

    def __call__(
        self, message: str, level: LogLevel = LogLevel.INFO, exception: bool = False
    ):
        self.log(message, level, exception)
