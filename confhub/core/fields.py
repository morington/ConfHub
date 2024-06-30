from typing import Type

from confhub.core.types import DataTypeMapping


class ConfigurationField:
    def __init__(
            self,
            data_type: Type,
            secret: bool,
            filename: str
    ) -> None:
        self.data_type = data_type
        self.secret = secret
        self.filename = filename

    def get_default_value(self) -> str:
        return f"{self.data_type.__name__}; {DataTypeMapping.get_default_value(self.data_type.__name__)}"


def field(
        data_type: Type,
        secret: bool = False,
        filename: str = None
) -> ConfigurationField:
    return ConfigurationField(
        data_type=data_type,
        secret=secret,
        filename=filename
    )
