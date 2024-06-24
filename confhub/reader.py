import os
from pathlib import Path
from typing import Optional, Any

import structlog
from dynaconf import Dynaconf, LazySettings
from dynaconf.utils.boxing import DynaBox

from confhub.enums import Service
from confhub.exceptions import PathError, ModuleException
from confhub.setup_logger import SetupLogger, LoggerReg

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class ReaderConf:
    """

    Class for reading configuration files.
    Supported configuration formats:
        - .toml - Default and recommended file format.
        - .yaml|.yml - Recommended for Django applications.
        - .json - Useful to reuse existing or exported settings.
        - .ini - Useful to reuse legacy settings.
        - .py - Not Recommended but supported for backwards compatibility.
        - .env - Useful to automate the loading of environment variables.

    It also allows you to specify separate `env` files for reading project environment variables.

    Methods:
    data_export(): Returns collected data in dictionary format.
    create_service_urls(): Finds services in the configuration and creates URLs for them.

    """
    def __init__(
            self,
            *paths: str | Path,
            dev: bool = False,
            logger_registrations: Optional[list[LoggerReg]] = None,
    ) -> None:
        """
        :param paths: str | Path - Configuration path
        :param dev: Local priority for configuration determination,
        :param logger_registrations: Logger configuration, default: LoggerReg(name="", level=LoggerReg.Level.DEBUG)
        """
        self.dev = dev
        PathError.checking_paths(*paths)
        settings_files = [*paths]

        try:
            PathError.checking_paths('.env')
        except PathError as _:
            logger.warning('The `.env` file was not found and will not be loaded!')

        __data: LazySettings = Dynaconf(settings_files=settings_files)

        try:
            self.is_dev = bool(__data.dev)
        except ValueError:
            logger.warning('Development clarification point is not set or is not of type `bool`', default_value=self.dev)
            self.is_dev = False

        self.data = self.data_export(data=__data)

        logger.debug('Loading logger parameters...')
        if logger_registrations is None:
            logger_registrations = [LoggerReg(name="", level=LoggerReg.Level.DEBUG)]

        SetupLogger(name_registration=logger_registrations, default_development=self.dev or self.is_dev)

    def data_export(self, data: LazySettings) -> dict:
        """
        Returns collected data in dictionary format

        :param data: LazySettings - LazySettings object
        :return: dict - collected data in dictionary format depending on development conditions
        """
        if self.is_dev or self.dev:
            __data: DynaBox = data.get('development')
        else:
            __data: DynaBox = data.get('release')

        if __data is None:
            raise ModuleException('The configuration is empty! Please check your configuration data.')

        return __data.to_dict()

    def create_service_urls(self) -> None:
        """
        Finds services in the configuration and creates URLs for them.

        :return: None
        """
        self.data.update({
            f"{service_name.value}_url": service_name.create_url(data=self.data.get(service_name.value))
            for service_name in Service
            if service_name.value in self.data
        })
