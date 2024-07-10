from pathlib import Path
from typing import List, Any, Dict, Optional

import yaml
import structlog

from confhub.core.block import BlockCore
from confhub.core.fields import ConfigurationField
from confhub.core.parsing import get_service_data, get_config_files, YamlFileMerger

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class ConfigurationBuilder:
    def __init__(self, *blocks: BlockCore):
        self.datafiles: Dict[str, Any] = {'settings': {}, '.secrets': {}}
        self.list_type_blocks: List[str] = []
        self.generate_filenames(*blocks)

    def generate_filenames(self, *blocks: BlockCore, parent_blocks: Optional[List[str]] = None, exclude: bool = True) -> None:
        if parent_blocks is None:
            parent_blocks = []

        def _process(params: Dict, parents: List[str]):
            # Перебираем все аттрибуты нашей модели
            for attr_name, attr_value in params.items():
                # Проверяем чтобы аттрибут точно был типа `field`
                if isinstance(attr_value, ConfigurationField):
                    # Расходимся на два пути, либо содержит Python тип, либо тип вложенной модели
                    if isinstance(attr_value.data_type, BlockCore):
                        if attr_value.is_list:
                            self.list_type_blocks.append(attr_value.data_type.__block__)

                        self.nested_model_processing(
                            field=attr_value,
                            parent_blocks=parents + [attr_name] + [attr_value.data_type.__block__]
                        )
                    else:
                        self.type_processing(
                            name=attr_name,
                            field=attr_value,
                            parent_blocks=parents
                        )

        # Перебираем все модели
        for block in blocks:
            # Исключаем те которые имеют аттрибут `__exclude__`, либо не являются пользовательской моделью
            if exclude:
                if not hasattr(block, '__exclude__') and block != BlockCore:
                    _process(params=block.__dict__, parents=parent_blocks + [block.__block__])
            else:
                if block != BlockCore:
                    _process(params=block.__class__.__dict__, parents=parent_blocks)

    def nested_model_processing(self, field: ConfigurationField, parent_blocks: List[str]):
        self.generate_filenames(field.data_type, parent_blocks=parent_blocks, exclude=False)

    def type_processing(self, name: str, field: ConfigurationField, parent_blocks: List[str]):
        if field.data_type == str:
            self.adding_field(
                name=name, value='str; VALUE; DEVELOPMENT_VALUE',
                parent_blocks=parent_blocks, secret=field.secret, filename=field.filename, is_list=field.is_list
            )
        elif field.data_type == int:
            self.adding_field(
                name=name, value='int; 1234; DEVELOPMENT_VALUE',
                parent_blocks=parent_blocks, secret=field.secret, filename=field.filename, is_list=field.is_list
            )
        elif field.data_type == float:
            self.adding_field(
                name=name, value='int; 1234.12; DEVELOPMENT_VALUE',
                parent_blocks=parent_blocks, secret=field.secret, filename=field.filename, is_list=field.is_list
            )
        elif field.data_type == bool:
            self.adding_field(
                name=name, value='int; True; DEVELOPMENT_VALUE',
                parent_blocks=parent_blocks, secret=field.secret, filename=field.filename, is_list=field.is_list
            )

    def adding_field(self, name: str, value: str, parent_blocks: List[str], is_list: bool, secret: bool = False, filename: Optional[str] = None):
        if secret:
            target = self.datafiles.get('.secrets')
        elif filename:
            if not self.datafiles.get(filename, None):
                self.datafiles[filename] = {}
            target = self.datafiles.get(filename)
        else:
            target = self.datafiles.get('settings')

        for block in parent_blocks:
            if isinstance(target, Dict):
                if block not in target:
                    target[block] = {} if block not in self.list_type_blocks else []
            elif isinstance(target, List):
                if not any(block in d for d in target):
                    target.append({block: {} if block not in self.list_type_blocks else []})

            if isinstance(target, Dict):
                target = target[block]
            elif isinstance(target, List):
                _search_data = [d for d in target if block in d]
                if _search_data:
                    target = _search_data[0][block]

        if isinstance(target, List):
            if is_list:
                target.append({name: [value]})
            else:
                target.append({name: value})
        elif isinstance(target, Dict):
            if is_list:
                target[name] = [value]
            else:
                target[name] = value
        print()

    @staticmethod
    def remove_empty_dicts(data):
        if isinstance(data, dict):
            return {k: ConfigurationBuilder.remove_empty_dicts(v) for k, v in data.items() if v and ConfigurationBuilder.remove_empty_dicts(v)}
        elif isinstance(data, list):
            return [ConfigurationBuilder.remove_empty_dicts(v) for v in data if v and ConfigurationBuilder.remove_empty_dicts(v)]
        return data

    def sync_to_new_dict(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        def sync_values(old: Any, new: Any) -> Any:
            if isinstance(old, dict) and isinstance(new, dict):
                for key in new:
                    if key in old:
                        new[key] = sync_values(old[key], new[key])
                    else:
                        new[key] = old.get(key, new[key])
                return new
            elif isinstance(old, list) and isinstance(new, list):
                for new_item in new.copy():
                    for old_item in old:
                        if isinstance(new_item, dict) and isinstance(old_item, dict):
                            if list(new_item.keys())[0] == list(old_item.keys())[0]:
                                new_item = sync_values(old_item, new_item)
                        elif isinstance(new_item, list) and isinstance(old_item, list) or isinstance(new_item, str) and isinstance(old_item, str):
                            new = old
                return new
            else:
                return old

        return sync_values(old_data, new_data)

    def create_files(self, config_path: Path) -> None:
        datafiles = self.remove_empty_dicts(self.datafiles)

        service_data: Dict[str, Any] = get_service_data()
        config_files: List[str | Path] = get_config_files(service_data=service_data)
        merger_data: Dict[str, Any] = YamlFileMerger(*config_files).data

        for filename, data in datafiles.items():
            file_path = config_path / Path(f'{filename}.yml')

            if merger_data:
                data_updated = self.sync_to_new_dict(merger_data, data)
            else:
                data_updated = data

            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data_updated, file, default_flow_style=False)

            logger.info("Create file", path=file_path)
