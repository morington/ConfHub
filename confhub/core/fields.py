from typing import Type, Any

from confhub.core.types import DataTypeMapping


class ConfigurationField:
    def __init__(
            self,
            data_type: Any,
            secret: bool,
            filename: str,
            is_list: bool
    ) -> None:
        self.data_type = data_type
        self.secret = secret
        self.filename = filename
        self.is_list = is_list

    def get_default_value(self) -> str:
        return f"{self.data_type.__name__}; {DataTypeMapping.get_default_value(self.data_type.__name__)}; DEVELOPMENT_VALUE"


def field(
        data_type: Any,
        secret: bool = False,
        filename: str = None,
        is_list: bool = False,
) -> ConfigurationField:
    return ConfigurationField(
        data_type=data_type,
        secret=secret,
        filename=filename,
        is_list=is_list,
    )
