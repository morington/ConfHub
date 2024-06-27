import sys
from pathlib import Path

from confhub.console import main
from confhub.__meta__ import __version__
from confhub.setup_logger import SetupLogger, LoggerReg

SetupLogger(
    name_registration=[
        LoggerReg(name="confhub", level=LoggerReg.Level.DEBUG),
    ],
    developer_mode=True
)

if __name__ == '__main__':
    project_path = Path.cwd()
    sys.path.append(str(project_path.resolve()))

    main(prog='confhub', version=__version__)
