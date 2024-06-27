from typing import Type

from confhub.core.types import DataTypeMapping


class ConfigurationField:
    def __init__(
            self,
            data_type: Type,
            secret: bool,
            filename: str,
            development_mode: bool
    ) -> None:
        self.data_type = data_type
        self.secret = secret
        self.filename = filename
        self.development_mode = development_mode

    def get_default_value(self) -> str:
        default_value = f"{self.data_type.__name__}; {DataTypeMapping.get_default_value(self.data_type.__name__)}"

        if self.development_mode:
            return f"{default_value}; DEVELOPMENT_{DataTypeMapping.get_default_value(self.data_type.__name__)}"
        return default_value


def field(
        data_type: Type,
        secret: bool = False,
        filename: str = None,
        development_mode: bool = False
) -> ConfigurationField:
    return ConfigurationField(
        data_type=data_type,
        secret=secret,
        filename=filename,
        development_mode=development_mode
    )
