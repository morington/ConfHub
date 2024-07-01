from pathlib import Path
from typing import List, Any, Dict, Type

import yaml
import structlog

from confhub.core.block import BlockCore
from confhub.core.error import ConfhubError
from confhub.core.fields import ConfigurationField
from confhub.utils.gitignore import add_to_gitignore

logger: structlog.BoundLogger = structlog.get_logger("confhub")


def has_configuration_fields(select_class: BlockCore) -> bool:
    if any(isinstance(item, ConfigurationField) for item in select_class.__dict__.values()):
        return True
    if any(isinstance(item, ConfigurationField) for item in select_class.__class__.__dict__.values()):
        return False
    raise ConfhubError("Cannot find field in model object", select_class=select_class)


class ConfigurationBuilder:
    def __init__(self, *blocks: BlockCore):
        self.blocks = list(blocks)
        self.datafiles: Dict[str, Any] = {'settings': {}, '.secrets': {}}
        self.generate_filenames()

    def data_typing(self, field: ConfigurationField) -> Any:
        if isinstance(field.data_type, BlockCore):
            nested_block = {
                nested_field_name: self.data_typing(nested_field)
                for nested_field_name, nested_field in field.data_type.__class__.__dict__.items()
                if isinstance(nested_field, ConfigurationField)
            }
            return [nested_block] if field.is_list else nested_block
        return [field.get_default_value()] if field.is_list else field.get_default_value()

    def new_nested(self, nested_model: Type[BlockCore]):
        nested_block = {nested_model.__block__: {}}
        for nested_field_name, nested_field in nested_model.__dict__.items():
            if isinstance(nested_field, ConfigurationField):
                nested_block[nested_model.__block__][nested_field_name] = (
                    [self.new_nested(nested_field.data_type.__class__)] if isinstance(nested_field.data_type, BlockCore) else
                    self.data_typing(nested_field)
                )
            elif isinstance(nested_field, BlockCore):
                nested_block[nested_model.__block__][nested_field_name] = [self.new_nested(nested_field.__class__)]
        return nested_block

    def add_field_to_datafiles(
            self, field_name: str, field: ConfigurationField, parent_path: List[str]
    ) -> None:
        if field.secret:
            target = self.datafiles['.secrets']
        elif field.filename:
            target = self.datafiles.setdefault(field.filename, {})
        else:
            target = self.datafiles['settings']

        current = target
        for part in parent_path:
            current = current.setdefault(part, {})

        if field.is_list and isinstance(field.data_type, BlockCore):
            current[field_name] = [self.new_nested(field.data_type.__class__)]
        elif field.is_list:
            current[field_name] = [field.get_default_value()]
        elif isinstance(field.data_type, BlockCore):
            current[field_name] = {
                nested_field_name: self.data_typing(nested_field)
                for nested_field_name, nested_field in field.data_type.__class__.__dict__.items()
                if isinstance(nested_field, ConfigurationField)
            }
        else:
            current[field_name] = field.get_default_value()

    def process_block(self, _block: BlockCore, parent_path: List[str], parent: str = None) -> None:
        if hasattr(_block, '__exclude__') and _block.__exclude__ and not parent:
            return

        current_path = parent_path + ([_block.__block__] if not parent else [parent])

        for field_name, field in (_block.__dict__.items() if has_configuration_fields(_block) else _block.__class__.__dict__.items()):
            if isinstance(field, ConfigurationField):
                if isinstance(field.data_type, BlockCore):
                    self.add_field_to_datafiles(field_name, field, current_path)
                    self.process_block(field.data_type, current_path + [field_name] if field.is_list else current_path, parent=field_name if not field.is_list else None)
                else:
                    self.add_field_to_datafiles(field_name, field, current_path)
            elif isinstance(field, BlockCore):
                self.process_block(field, current_path, parent=field_name)

    def generate_filenames(self):
        for block in self.blocks:
            if block != BlockCore:
                self.process_block(block, [])

    @staticmethod
    def remove_empty_dicts(data):
        if isinstance(data, dict):
            return {k: ConfigurationBuilder.remove_empty_dicts(v) for k, v in data.items() if v and ConfigurationBuilder.remove_empty_dicts(v)}
        elif isinstance(data, list):
            return [ConfigurationBuilder.remove_empty_dicts(v) for v in data if v and ConfigurationBuilder.remove_empty_dicts(v)]
        return data

    def create_files(self, config_path: Path) -> None:
        datafiles = self.remove_empty_dicts(self.datafiles)
        for filename, data in datafiles.items():
            file_path = config_path / f'{filename}.yml'

            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as file:
                    yaml_data = yaml.safe_load(file)
                    if yaml_data:
                        for key, value in data.items():
                            if key in yaml_data and isinstance(yaml_data[key], dict):
                                yaml_data[key].update(value)
                                data[key] = yaml_data[key]

            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False)

            if filename.startswith('.'):
                add_to_gitignore(f"{filename}.*")

            logger.info("Create file", path=file_path)
