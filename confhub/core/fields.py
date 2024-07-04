from typing import Any

from confhub.core.types import DataTypeMapping


class ConfigurationField:
    def __init__(
            self,
            data_type: Any,
            secret: bool,
            filename: str,
            is_list: bool,
    ) -> None:
        self.data_type = data_type
        self.secret = secret
        self.filename = filename
        self.is_list = is_list

    def __str__(self) -> str:
        return f"ConfigurationField: [{self.data_type}]"

    def __repr__(self) -> str:
        return f"ConfigurationField: [{self.data_type}; secret={self.secret}; filename={self.filename}; is_list={self.is_list}]"

    def get_default_value(self) -> str:
        return f"{self.data_type.__name__}; {DataTypeMapping.get_default_value(self.data_type.__name__)}"


def field(
        data_type: Any,
        secret: bool = False,
        filename: str = None,
        is_list: bool = False
) -> ConfigurationField:
    return ConfigurationField(
        data_type=data_type,
        secret=secret,
        filename=filename,
        is_list=is_list
    )


def exclude(cls):
    cls.__exclude__ = True
    return cls
