"""
Logging Configuration

This configuration sets up struct logging with the help of the
structlog and logging libraries.

Main features:
    - Separation of logs by loggers for modules/components of the project.
    - Convenient syntax for writing logs through loggers.
    - Possibility to write logs to a file.
    - Automatic logging to JSON format when working in Docker if
    DEV environment variable is not set.

Structlog processors add useful information to logs such as
request ID, time, log level, etc.

Configuration allows you to efficiently log application events and
debug its operation.


setup_logger.py developed by morington
https://gist.github.com/morington/906cbc6fca128bde4ab81fb8e8eed849
"""
import os
import sys
import logging
import logging.config
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List

import structlog
from structlog.typing import EventDict


""" Constants for defining the names of handlers and formatters """
CONSOLE_HANDLER: str = "console"
CONSOLE_FORMATTER: str = "console_formatter"

JSONFORMAT_HANDLER: str = "jsonformat"
JSONFORMAT_FORMATTER: str = "jsonformat_formatter"


def logger_detailed(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    A function for detailing logs, adding information about the file, function and line number.
    Parameters:
    logger (logging.Logger): Logger for recording logs.
    method_name (str): Method name.
    event_dict (EventDict): Event dictionary for logging.
    Returns:
    EventDict: Augmented event dictionary.
    """
    filename: str = event_dict.pop("filename")
    func_name: str = event_dict.pop("func_name")
    lineno: str = event_dict.pop("lineno")

    event_dict["logger"] = f"{filename}:{func_name}:{lineno}"

    return event_dict


@dataclass
class LoggerReg:
    """
    Class for representing logger settings.
    Attributes:
    name (str): Logger name.
    level (Level): Logging level.
    propagate (bool): Flag to indicate whether messages should be passed to parent loggers. Default is False.
    write_file (bool): Flag to indicate whether logs should be written to a file. Default is True.
    """
    class Level(Enum):
        DEBUG: str = "DEBUG"
        INFO: str = "INFO"
        WARNING: str = "WARNING"
        ERROR: str = "ERROR"
        CRITICAL: str = "CRITICAL"
        NONE: str = None

    name: str
    level: Level = Level.DEBUG
    propagate: bool = False
    write_file: bool = False


class SetupLogger:
    """

    Class for setting up logging using structlog.
    Attributes:
    name_registration (List[LoggerReg]): List of logger settings.
    default_development (bool): Flag to indicate the development mode, forces the output format to be CONSOLE. Default is False.
    log_to_file (bool): Flag to indicate that logs are written to a file. Default is False.
    logs_dir (str): Directory for writing logs. Default is "logs".

    Methods:
    __str__(): Returns a string representation of the class.
    __repr__(): Returns the class representation as a string.
    renderer(): Returns the logging format depending on the conditions.
    timestamper(): Returns a TimeStamper object for the logger timestamp.
    preprocessors(addit: bool = False): Setting up structlog preprocessors.
    init_structlog(): Initializes logging settings using structlog.

    """

    def __init__(
            self,
            name_registration: Optional[List[LoggerReg]],
            developer_mode: bool = False,
            log_to_file: bool = False,
            logs_dir: str = "logs",
            file_write_format: str = JSONFORMAT_FORMATTER
    ) -> None:
        self.name_registration = [LoggerReg(name="", level=LoggerReg.Level.DEBUG)] if name_registration is None else name_registration
        self.name_registration.extend([LoggerReg(name="confhub", level=LoggerReg.Level.INFO)])
        self.developer_mode = developer_mode
        self.log_to_file = log_to_file
        self.logs_dir = logs_dir
        self.file_write_format = file_write_format
        self.module_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.init_structlog()

    def __str__(self) -> str:
        return f"<{__class__.__name__} dev:{sys.stderr.isatty()}; Reg {len(self.name_registration)} loggers>"

    def __repr__(self):
        return self.__str__()

    @property
    def renderer(self) -> str:
        """
        Returns the logging format depending on the conditions.
        Returns:
        str: Format.
        """
        if sys.stderr.isatty() or os.environ.get("DEV", self.developer_mode):
            return CONSOLE_HANDLER
        return JSONFORMAT_HANDLER

    @property
    def timestamper(self) -> structlog.processors.TimeStamper:
        """
        Returns a TimeStamper object for the logger timestamp.
        Returns:
        structlog.processors.TimeStamper: TimeStamper object.
        """
        return structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

    def preprocessors(self, addit: bool = False) -> List[any]:
        """
        Setting up structlog preprocessors.
        Parameters:
        addit (bool): Flag for additional handlers. Default is False.
        Returns:
        List[any]: List of preprocessors.
        """
        preprocessors: List[any] = [
            self.timestamper,
            structlog.stdlib.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            logger_detailed,
        ]
        if addit:
            preprocessors: List[any] = (
                    [
                        structlog.contextvars.merge_contextvars,
                        structlog.stdlib.filter_by_level,
                    ]
                    + preprocessors
                    + [
                        structlog.stdlib.PositionalArgumentsFormatter(),
                        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                    ]
            )
        return preprocessors

    def init_structlog(self):
        """ Initializes logging settings using structlog. """
        handlers = {
            CONSOLE_HANDLER: {
                "class": "logging.StreamHandler",
                "formatter": CONSOLE_FORMATTER,
            },
            JSONFORMAT_HANDLER: {
                "class": "logging.StreamHandler",
                "formatter": JSONFORMAT_FORMATTER,
            },
        }

        if self.log_to_file:
            module_logs_dir = os.path.join(self.logs_dir, self.module_name)
            os.makedirs(module_logs_dir, exist_ok=True)
            log_filename = f"{module_logs_dir}/{datetime.now().strftime('%d.%m.%Y_%H_%M_%S')}.log"

            file_handler = {
                "class": "logging.FileHandler",
                "filename": log_filename,
                "formatter": self.file_write_format,
            }
            handlers['file_handler'] = file_handler

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    JSONFORMAT_FORMATTER: {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processor": structlog.processors.JSONRenderer(),
                        "foreign_pre_chain": self.preprocessors(),
                    },
                    CONSOLE_FORMATTER: {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processor": structlog.dev.ConsoleRenderer(),
                        "foreign_pre_chain": self.preprocessors(),
                    },
                },
                "handlers": handlers,
                "loggers": {
                    f"{logger_setting.name}": {
                        "handlers": [self.renderer] + ["file_handler"] if logger_setting.write_file else [self.renderer],
                        "level": logger_setting.level.value,
                        "propagate": logger_setting.propagate,
                    }
                    for logger_setting in self.name_registration
                },
            }
        )

        structlog.configure(
            processors=self.preprocessors(True),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
