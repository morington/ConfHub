import dataclasses
import fnmatch
from pathlib import Path
from typing import Optional, Type, List

import structlog

from confhub import BlockCore
from confhub.core.parsing import get_service_data, YamlFileMerger
from confhub.setup_logger import SetupLogger, LoggerReg
from confhub.utils.__models import get_models_from_path

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class Confhub:
    def __init__(
            self,
            developer_mode: bool = False,
            logger_regs: Optional[list[LoggerReg]] = None,
    ) -> None:
        """
        Example:
        import dataclasses

        from confhub import Confhub

        if __name__ == '__main__':
            data: type[dataclasses.dataclass] = Confhub(developer_mode=False).models

            print(data.postgresql.host)
        """
        service_data = get_service_data()
        _config_path = service_data.get('configs_path')
        if not _config_path or not isinstance(_config_path, str):
            raise ValueError("Directory `config` not defined")

        self.developer_mode = developer_mode if developer_mode else service_data.get('developer_mode')
        if self.developer_mode:
            logger.warning('Developer mode enabled for configuration')

        SetupLogger(name_registration=logger_regs, developer_mode=developer_mode)

        models: List[BlockCore] = get_models_from_path(data=service_data)

        config_path = Path(service_data.get('configs_path'))
        config_list = list(config_path.glob('*'))
        filtered_config_list = [file for file in config_list if not fnmatch.fnmatch(file.name, 'example__*')]

        self.models = self.__load(*models, files=filtered_config_list)

    def __load(self, *models: BlockCore, files: List[str | Path]) -> Type[dataclasses.dataclass]:
        merger = YamlFileMerger(*files)

        __fields_from_dataclass = []
        for block in models:
            value = block.from_dict(merger.data.get(block.__block__), development_mode=self.developer_mode)

            if not value:
                continue

            __fields_from_dataclass.append((block.__block__, type(block), dataclasses.field(default=value)))

        return dataclasses.make_dataclass('Data', __fields_from_dataclass)


if __name__ == '__main__':
    data = Confhub().models
    print()
