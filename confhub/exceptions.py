from pathlib import Path
from typing import Any, Type

import structlog

logger: structlog.BoundLogger = structlog.get_logger("exceptions")


class ModuleException(Exception):
    def __init__(self, message: str, *args, **kwargs) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        data_attrs = {
            attr: getattr(self, attr)
            for attr in self.__dict__
            if (
                not callable(getattr(self, attr)) or isinstance(getattr(self, attr), type)
            ) and attr != 'message'
        }
        logger.debug(self.message, **data_attrs)
        return self.message


class PathError(ModuleException):
    def __init__(
            self,
            wrong_paths: list,
            message: str = "The path is incorrect"
    ) -> None:
        self.message = message
        self.wrong_paths = wrong_paths
        super().__init__(message)

    @staticmethod
    def checking_paths(*paths: str) -> None:
        checking = [path for path in paths if not Path(path).exists()]
        if checking:
            raise PathError(wrong_paths=checking)


class ModelConfigError(ModuleException):
    def __init__(self, item: Any, item_type: type, message: str = 'Model config is incorrect') -> None:
        self.item = item
        self.item_type = item_type
        self.message = message
        super().__init__(message)
