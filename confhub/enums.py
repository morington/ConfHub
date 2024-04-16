from enum import Enum

import structlog

from confhub.models import URLConfig

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class Schemes(Enum):
    POSTGRESQL = "postgresql+asyncpg"
    REDIS = "redis"
    NATS = "nats"
    KAFKA = "kafka"
    CELERY = "http"
    RABBITMQ = "amqp"
    INFLUXDB = "http"


class Service(Enum):
    POSTGRESQL = "POSTGRESQL"
    REDIS = "REDIS"
    NATS = "NATS"
    KAFKA = "KAFKA"
    CELERY = "CELERY"
    RABBITMQ = "RABBITMQ"
    INFLUXDB = "INFLUXDB"

    def get_scheme(self) -> str:
        return Schemes[self.value].value

    def create_url(self, data: dict[str, str | int]) -> str:
        __config = URLConfig(scheme=self.get_scheme(), **data)
        url = __config.get_human_url()
        logger.debug('Created URL service', url=url, service=self.value)

        return url
