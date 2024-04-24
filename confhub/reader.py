import os
from pathlib import Path

import structlog
from dynaconf import Dynaconf, LazySettings
from dynaconf.utils.boxing import DynaBox

from confhub.enums import Service
from confhub.exceptions import PathError, ModuleException
from confhub.setup_logger import SetupLogger, LoggerReg

SetupLogger(
    name_registration=[
        LoggerReg(name="confhub", level=LoggerReg.Level.DEBUG),
        LoggerReg(name="exceptions", level=LoggerReg.Level.DEBUG)
    ],
    default_development=True
)
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
    def __init__(self, *paths: str | Path, env: str | Path = '.env', dev: bool = False) -> None:
        """

        :param paths: str | Path - Configuration path
        :param env: str| Path - Path to the project environment variable file
        :param dev: Local priority for configuration determination
        """
        self.dev = dev
        PathError.checking_paths(*paths)
        settings_files = [*paths]

        try:
            PathError.checking_paths(env)
            settings_files.append(env)
        except PathError as _:
            logger.warning('The `.env` file was not found and will not be loaded!', env_path=env)

        __data: LazySettings = Dynaconf(
            load_dotenv=True,
            settings_files=settings_files
        )

        self.data = self.data_export(data=__data)

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} env={self.__load_env}>'
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} env={self.__load_env} paths={self.__paths}'

    def data_export(self, data: LazySettings) -> dict:
        """
        Returns collected data in dictionary format

        :param data: LazySettings - LazySettings object
        :return: dict - collected data in dictionary format depending on development conditions
        """
        if os.getenv('DEV', False) or self.dev:
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
