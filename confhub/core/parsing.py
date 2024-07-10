import fnmatch
from typing import Union, Any, Dict, List

import yaml
import structlog
from pathlib import Path

from confhub.core.types import convert_value

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class YamlFileMerger:
    def __init__(self, *paths: str | Path):
        self.paths = [Path(path) for path in paths]
        self.data = self.merge_files()

    def merge_files(self) -> Dict[str, Any]:
        merged_data = {}
        for file_path in self.paths:
            try:
                with open(file_path, 'r') as file:
                    data = yaml.safe_load(file)
                    merged_data = self.merge_dicts(merged_data, data)
            except FileNotFoundError:
                logger.info(f"File not found: {file_path}")
            except yaml.YAMLError as e:
                logger.info(f"Error parsing YAML from {file_path}: {e}")

        return merged_data

    def merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        if dict2:
            for key, value in dict2.items():
                if key in dict1:
                    if isinstance(dict1[key], dict) and isinstance(value, dict):
                        dict1[key] = self.merge_dicts(dict1[key], value)
                    elif isinstance(dict1[key], list) and isinstance(value, list):
                        dict1[key] = self.merge_lists(dict1[key], value)
                    else:
                        dict1[key] = value
                else:
                    dict1[key] = value

        return dict1

    def merge_lists(self, list1: List[Any], list2: List[Any]) -> List[Any]:
        for item2 in list2:
            if isinstance(item2, dict):
                matched = False
                for item1 in list1:
                    if isinstance(item1, dict) and self.have_common_keys(item1, item2):
                        self.merge_dicts(item1, item2)
                        matched = True
                        break
                if not matched:
                    list1.append(item2)
            else:
                if item2 not in list1:
                    list1.append(item2)
        return list1

    def have_common_keys(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> bool:
        return any(key in dict1 for key in dict2)


def find_project_root(start_path, markers):
    current_path = Path(start_path).resolve()
    while current_path != current_path.root:
        if any((current_path / marker).exists() for marker in markers):
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"None of the markers '{markers}' found in any parent directories.")


def get_service_data() -> Dict[str, Any]:
    root_path = find_project_root(Path.cwd(), ['.gitignore', 'README.md', 'requirements.txt'])
    yml_data = YamlFileMerger(root_path / '.service.yml')
    return yml_data.data


def get_config_files(service_data: Dict[str, Any]) -> List[str | Path]:
    config_path = Path(service_data.get('configs_path'))
    config_list = list(config_path.glob('*'))
    return [file for file in config_list if not fnmatch.fnmatch(file.name, 'example__*')]


def parsing_value(value: str | List, development_mode: bool) -> Union[str, int, float, bool, List]:
    if isinstance(value, List):
        return [parsing_value(_value, development_mode) for _value in value]
    elif isinstance(value, str):
        metadata = value.split(';')

        if len(metadata) < 2:
            raise ValueError("Value metadata contains little or no data")

        type_value, value, *development_value = metadata + [None] * (3 - len(metadata))
        development_value = development_value[0] if development_value else None

        return convert_value(type_value, development_value.strip() if development_value and development_mode else value.strip())
