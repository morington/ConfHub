from typing import Union, Any, Dict, List

import yaml
from pathlib import Path

from confhub.core.types import convert_value


def merge_dicts(base_dict, new_dict):
    for key in new_dict:
        if key in base_dict:
            if isinstance(base_dict[key], dict) and isinstance(new_dict[key], dict):
                merge_dicts(base_dict[key], new_dict[key])
            else:
                base_dict[key] = new_dict[key]
        else:
            base_dict[key] = new_dict[key]
    return base_dict


class YamlFileMerger:
    def __init__(self, *paths: str | Path):
        self.paths = [Path(path) for path in paths]
        self.data = self.merge_files()

    def merge_files(self):
        merged_data = {}
        for file_path in self.paths:
            try:
                with open(file_path, 'r') as file:
                    data = yaml.safe_load(file)
                    merged_data = merge_dicts(merged_data, data)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except yaml.YAMLError as e:
                print(f"Error parsing YAML from {file_path}: {e}")

        return merged_data


def get_service_data() -> Dict[str, Any]:
    root_path = Path.cwd()
    yml_data = YamlFileMerger(root_path / '.service.yml')
    return yml_data.data


def parsing_value(value: str, development_mode: bool) -> Union[str, int, float, bool]:
    if isinstance(value, List):
        return [parsing_value(_value, development_mode) for _value in value]
    else:
        metadata = value.split(';')

        if len(metadata) < 2:
            raise ValueError("Value metadata contains little or no data")

        type_value, value, *development_value = metadata + [None] * (3 - len(metadata))
        development_value = development_value[0] if development_value else None

        return convert_value(type_value, development_value.strip() if development_value and development_mode else value.strip())
