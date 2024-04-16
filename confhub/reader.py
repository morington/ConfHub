import os
from pathlib import Path

import structlog
from dynaconf import Dynaconf, LazySettings

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
    def __init__(self, *paths: str | Path, env: str = '.env', dev: bool = False) -> None:
        PathError.checking_paths(*paths)
        settings_files = [*paths]

        try:
            PathError.checking_paths(env)
            settings_files.append(env)
        except PathError as _:
            logger.warning('The `.env` file was not found and will not be loaded!', env_path=env)

        _data: LazySettings = Dynaconf(
            load_dotenv=True,
            settings_files=settings_files
        )

        if os.getenv('DEV', dev):
            self.data = _data.get('development')
        else:
            self.data = _data.get('release')

        if self.data is None:
            raise ModuleException('The configuration is empty! Please check your configuration data.')

    def create_service_urls(self) -> None:
        for service_name in Service:
            if service_name.value in self.data:
                self.data.update({
                    f"{service_name.value.lower()}_url": service_name.create_url(
                        data=self.data.get(service_name.value).to_dict()
                    )
                })
