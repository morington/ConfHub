import argparse

import structlog

import confhub.commands as commands
from confhub.setup_logger import SetupLogger, LoggerReg
from confhub.__meta__ import __version__

SetupLogger(
    name_registration=[
        LoggerReg(name="confhub_configuration", level=LoggerReg.Level.INFO),
    ],
    default_development=True
)
logger: structlog.BoundLogger = structlog.getLogger('confhub_configuration')


class Config:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=f"Confhub v{__version__} help")
        self.init_args()

        self.__args = self.parser.parse_args()
        logger.debug('Initializing config')

    def parsing(self) -> None:
        logger.debug('Argument handling..')

        if self.__args.create:
            commands.create(folder=self.__args.create)

        logger.debug('Argument processing completed!')

    def init_args(self):
        # Добавляем аргументы
        self.parser.add_argument(
            '-c', '--create',
            metavar="folder", type=str,
            help='Generating configuration files'
        )


def main() -> None:
    config = Config()
    config.parsing()


if __name__ == '__main__':
    main()
