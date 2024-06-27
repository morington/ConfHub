from pathlib import Path
from typing import List

import structlog

from confhub import templates, BlockCore
from confhub.builder import ConfigurationBuilder
from confhub.core.error import ConfhubError
from confhub.core.parsing import get_service_data
from confhub.utils.__models import get_models_from_path
from confhub.utils.gitignore import add_to_gitignore

logger: structlog.BoundLogger = structlog.getLogger('confhub')


def init(folder: str) -> None:
    """
    Initializes the project in the confhub system, creating the specified folder and generating all the necessary information in it.
    """
    if folder is None:
        raise ConfhubError("Path not specified for initialization")

    root_path = Path.cwd()
    project_folder = root_path / folder

    def create_folder_if_not_exists(path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def write_file(path: Path, content: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    create_folder_if_not_exists(project_folder)

    config_path = project_folder / 'config'
    create_folder_if_not_exists(config_path)

    models_file = project_folder / 'models.py'
    if not models_file.exists():
        write_file(models_file, templates.SAMPLE_MODELS)

    service_file = root_path / '.service.yml'
    service_content = templates.SERVICE.format(
        models_path=models_file.relative_to(root_path),
        configs_path=config_path.relative_to(root_path)
    )
    write_file(service_file, service_content)
    add_to_gitignore('.service.*')

    init_file = project_folder / '__init__.py'
    write_file(init_file, templates.INIT_SAMPLE)

    logger.info("Files have been successfully generated and are ready to use")


def generate_models() -> None:
    """
    Receives models from a models file and generates a configuration based on them.
    """
    service_data = get_service_data()

    models: List[BlockCore] = get_models_from_path(data=service_data)

    _config_path = service_data.get('configs_path')
    if not _config_path or not isinstance(_config_path, str):
        raise ValueError("Directory `config` not defined")

    ConfigurationBuilder(*models).create_files(Path.cwd() / Path(_config_path))

    add_to_gitignore('.secrets.*')

    logger.info("Configuration successfully generated")
