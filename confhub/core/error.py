import sys

import structlog

logger: structlog.BoundLogger = structlog.getLogger("confhub")


class ConfhubError(Exception):
    ...


def confhub_error(message: str, **kwargs) -> None:
    logger.error("Failed!", message=message, **kwargs)
    sys.exit(-1)
