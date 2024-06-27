from confhub.core.fields import ConfigurationField
from confhub.core.parsing import parsing_value


class BlockCore:
    __block__ = None

    @classmethod
    def from_dict(cls, data: dict, development_mode: bool):
        if data:
            instance = cls()

            for attr_name, attr_value in instance.__class__.__dict__.items():
                if isinstance(attr_value, ConfigurationField):
                    value_str = data.get(attr_name)
                    if value_str is not None:
                        value = parsing_value(value_str, development_mode)
                        setattr(instance, attr_name, value)
                    else:
                        raise ValueError(f"The value for `{cls.__block__}.{attr_name}` could not be found, perhaps the file was not transferred")
                elif isinstance(attr_value, BlockCore):
                    setattr(instance, attr_name, attr_value.from_dict(data.get(attr_value.__block__), development_mode))

            return instance
