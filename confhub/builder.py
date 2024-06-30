from pathlib import Path
from typing import List, Any, Dict, Optional

import yaml
import structlog

from confhub.core.block import BlockCore
from confhub.core.error import ConfhubError
from confhub.core.fields import ConfigurationField
from confhub.utils.gitignore import add_to_gitignore

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class ConfigurationBuilder:
    def __init__(self, *blocks: BlockCore):
        self.blocks = [*blocks]
        self.datafiles: Dict[str, Any] = self.generate_filenames()

    def generate_filenames(self) -> Dict[str, Any]:
        _datafiles = {'settings': {}, '.secrets': {}}

        def data_typing(field: ConfigurationField) -> Any:
            if field.is_list:
                return [field.get_default_value()]

            return field.get_default_value()

        def add_field_to_datafiles(
                field_name: str, field: ConfigurationField, parent_path: List[str]
        ) -> None:
            if field.secret:
                target = _datafiles['.secrets']
            elif field.filename:
                if field.filename not in _datafiles:
                    _datafiles[field.filename] = {}
                target = _datafiles[field.filename]
            else:
                target = _datafiles['settings']

            current = target
            for part in parent_path:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[field_name] = data_typing(field)

        def has_configuration_fields(select_class: BlockCore) -> bool:
            if any(isinstance(item, ConfigurationField) for item in [
                value for name, value in select_class.__dict__.items()
            ]):
                return True
            else:
                if any(isinstance(item, ConfigurationField) for item in [
                    value for name, value in select_class.__class__.__dict__.items()
                ]):
                    return False
                else:
                    raise ConfhubError("Cannot find field in model object", select_class=select_class)

        def process_block(_block: BlockCore, parent_path: List[str], parent: str = None) -> None:
            if hasattr(_block, '__exclude__') and _block.__exclude__ and not parent:
                return

            current_path = parent_path + [_block.__block__ if not parent else parent]
            if parent:
                current_path += [_block.__block__]

            # field.is_list
            for field_name, field in (_block.__dict__.items() if has_configuration_fields(_block) else _block.__class__.__dict__.items()):
                if isinstance(field, ConfigurationField):
                    if isinstance(field.data_type, BlockCore):
                        process_block(field.data_type, current_path, parent=field_name)
                    else:
                        add_field_to_datafiles(field_name, field, current_path)
                elif isinstance(field, BlockCore):
                    process_block(field, current_path, parent=field_name)

        for block in self.blocks:
            if block != BlockCore:
                process_block(block, [])

        return _datafiles

    def create_files(self, config_path: Path) -> None:
        for filename, data in self.datafiles.items():
            file_path = config_path / Path(f'{filename}.yml')

            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as file:
                    yaml_data = yaml.safe_load(file)

                    if yaml_data:
                        for key in data:
                            if key in yaml_data:
                                if not isinstance(yaml_data[key], Dict):
                                    for inner_key in data[key]:
                                        if inner_key in yaml_data[key]:
                                            if isinstance(data[key][inner_key], type(yaml_data[key][inner_key])):
                                                data[key][inner_key] = yaml_data[key][inner_key]

            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False)

            if filename.startswith('.'):
                add_to_gitignore(f"{filename}.*")

            logger.info("Create file", path=file_path)
