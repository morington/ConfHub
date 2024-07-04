from pathlib import Path
from typing import List, Any, Dict, Optional

import yaml
import structlog

from confhub.core.block import BlockCore
from confhub.core.fields import ConfigurationField

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class ConfigurationBuilder:
    def __init__(self, *blocks: BlockCore):
        self.datafiles: Dict[str, Any] = {'settings': {}, '.secrets': {}}
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
                        parents += [attr_name]
                        self.nested_model_processing(
                            field=attr_value,
                            parent_blocks=parents
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
            self.adding_field(name=name, value='str; VALUE; DEVELOPMENT_VALUE', parent_blocks=parent_blocks, secret=field.secret, filename=field.filename)
        elif field.data_type == int:
            self.adding_field(name=name, value='int; 1234; DEVELOPMENT_VALUE', parent_blocks=parent_blocks, secret=field.secret, filename=field.filename)
        elif field.data_type == float:
            self.adding_field(name=name, value='int; 1234.12; DEVELOPMENT_VALUE', parent_blocks=parent_blocks, secret=field.secret, filename=field.filename)
        elif field.data_type == bool:
            self.adding_field(name=name, value='int; True; DEVELOPMENT_VALUE', parent_blocks=parent_blocks, secret=field.secret, filename=field.filename)

    def adding_field(self, name: str, value: str, parent_blocks: List[str], secret: bool = False, filename: Optional[str] = None):
        if secret:
            target = self.datafiles.get('.secrets')
        elif filename:
            self.datafiles[filename] = {}
            target = self.datafiles.get(filename)
        else:
            target = self.datafiles.get('settings')

        for block in parent_blocks:
            if block not in target:
                target[block] = {}

            target = target[block]

        target[name] = value

    def create_files(self, config_path: Path) -> None:
        def update_nested_dict(new_data, old_data):
            for key, value in old_data.items():
                if isinstance(value, dict):
                    # Рекурсивно обновляем вложенные словари
                    if key in new_data:
                        update_nested_dict(new_data[key], value)
                else:
                    # Обновляем значения, если ключ существует
                    if key in new_data:
                        new_data[key] = value
            return new_data

        for filename, data in self.datafiles.items():
            file_path = config_path / Path(f'{filename}.yml')

            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as file:
                    data_old_file = yaml.safe_load(file)

                    if data_old_file:
                        data = update_nested_dict(data, data_old_file)

            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False)

            logger.info("Create file", path=file_path)
