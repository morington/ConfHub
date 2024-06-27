import importlib
from pathlib import Path
from typing import List, Dict, Any

import structlog

from confhub import BlockCore

logger: structlog.BoundLogger = structlog.get_logger("confhub")


def get_models_from_path(data: Dict[str, Any]) -> List[BlockCore]:
    module_path = Path(data.get('models_path'))
    module_name = '.'.join(module_path.parts[-2:]).replace('.py', '')

    logger.debug('Module path', path=module_path, name=module_name)

    module = importlib.import_module(module_name)
    return [
        getattr(module, attr)
        for attr in dir(module)
        if isinstance(getattr(module, attr), type) and issubclass(getattr(module, attr), BlockCore)
    ]
