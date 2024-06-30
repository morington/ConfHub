import sys

import structlog

logger: structlog.BoundLogger = structlog.getLogger("confhub")


class ConfhubError(Exception):
    def __init__(self, message, **kwargs):
        logger.error(message, exc_info=True, **kwargs)

        super().__init__(message)


def confhub_error(message: str, **kwargs) -> None:
    logger.error("Failed!", message=message, **kwargs)
    sys.exit(-1)
