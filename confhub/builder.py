from pathlib import Path
from typing import List, Any, Dict

import yaml
import structlog

from confhub.core.block import BlockCore
from confhub.core.fields import ConfigurationField

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class ConfigurationBuilder:
    def __init__(self, *blocks: BlockCore):
        self.blocks = [*blocks]
        self.datafiles: Dict[str, Any] = self.generate_filenames()

    def generate_filenames(self) -> Dict[str, Any]:
        _datafiles = {'settings': {}, '.secrets': {}}

        def add_field_to_datafiles(field_name: str, field: ConfigurationField, parent_path: List[str]) -> None:
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

            current[field_name] = field.get_default_value()

        def process_block(_block: BlockCore, parent_path: List[str]) -> None:
            current_path = parent_path + [_block.__block__]

            for field_name, field in _block.__dict__.items():
                if isinstance(field, ConfigurationField):
                    add_field_to_datafiles(field_name, field, current_path)
                elif isinstance(field, BlockCore):
                    process_block(field, current_path)

        for block in self.blocks:
            process_block(block, [])

        return _datafiles

    def create_files(self, config_path: Path) -> None:
        for filename, data in self.datafiles.items():
            file_path = config_path / Path(f'{filename}.yml')

            existing_file = None
            if file_path.exists():
                while existing_file is None:
                    result = input(f"The `{file_path}` file already exists, should I recreate it? [Y/n] ")

                    if result.lower() in ['y', 'n', '', ' ']:
                        if result.lower() == 'n':
                            existing_file = False
                        else:
                            existing_file = True

            if existing_file:
                with open(file_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data, file, default_flow_style=False)

                logger.info("Create file", path=file_path)
            else:
                logger.info('Skip...', path=file_path)