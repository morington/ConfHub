import os
from pathlib import Path

import structlog

import confhub.templates as templates

logger: structlog.BoundLogger = structlog.getLogger('confhub_configuration')


def create(folder: str) -> None:
    def generate_configurations_files(select_folder: Path) -> None:
        if not select_folder.exists():
            select_folder.mkdir(parents=True, exist_ok=True)
            logger.debug('Create folder', path=select_folder)

        """ SECRETS CONFIGURATION FILE """
        secret_file = folder_path / '.secrets.yml'
        with open(secret_file, 'w', encoding='utf-8') as f:
            f.write(templates.SECRETS)

        """ SECRETS EXAMPLE CONFIGURATION FILE """
        secret_file__example = folder_path / 'example__secrets.yml'
        with open(secret_file__example, 'w', encoding='utf-8') as f:
            f.write(templates.SECRETS_EXAMPLE)

        """ SETTINGS CONFIGURATION FILE """
        settings_file = folder_path / 'settings.yml'
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(templates.SETTINGS)

        logger.info('Loading configuration files', secret_file=secret_file, secret_file__example=secret_file__example, settings=settings_file)

    current_dir = Path(os.getcwd())
    folder_path = current_dir / Path(folder)
    logger.debug('`create` function called', folder=folder_path, current_dir=current_dir)

    if not folder_path.exists():
        _q = True
        while _q:
            confirmation_creation_folder = input(f'\nDo you want to create a new folder at ({folder_path})? [Y/n]\n: ')
            if not confirmation_creation_folder:
                confirmation_creation_folder = 'y'

            if confirmation_creation_folder.lower() in ['y', 'yes', 'д', 'да']:
                _q = False
                folder_path.mkdir(parents=True, exist_ok=True)
                generate_configurations_files(select_folder=folder_path)
            elif confirmation_creation_folder.lower() in ['n', 'no', 'н', 'нет']:
                _q = False
                logger.info('Generation canceled')
    else:
        generate_configurations_files(select_folder=folder_path)
        logger.debug('Folder exists')
