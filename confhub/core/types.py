from typing import Type, Union


MAPPING = {
    "str": (str, "VALUE"),
    "int": (int, "1234"),
    "float": (float, "1234.101"),
    "bool": (bool, "true"),
}


class DataTypeMapping:
    @classmethod
    def get_default_value(cls, type_name: str) -> str:
        if type_name not in MAPPING:
            raise ValueError(f"Unknown data type: {type_name}")

        return MAPPING.get(type_name)[1]

    @classmethod
    def get_data_type(cls, type_name: str) -> Type:
        if type_name not in MAPPING:
            raise ValueError(f"Unknown data type: {type_name}")

        return MAPPING.get(type_name)[0]


def convert_value(type_name: str, value: str) -> Union[str, int, float, bool]:
    if type_name == "bool":
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            raise ValueError(f"Cannot convert string '{value}' to bool")
    else:
        try:
            return MAPPING.get(type_name)[0](value)
        except ValueError:
            raise ValueError(f"Cannot convert `{value}` to type {type_name}")
