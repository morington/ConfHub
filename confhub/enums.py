from enum import Enum

import structlog

from confhub.models import URLConfig

logger: structlog.BoundLogger = structlog.get_logger("confhub")


class Schemes(Enum):
    postgresql = "postgresql+asyncpg"
    redis = "redis"
    nats = "nats"
    kafka = "kafka"
    celery = "http"
    rabbitmq = "amqp"
    influxdb = "http"


class Service(Enum):
    postgresql = "postgresql"
    redis = "redis"
    nats = "nats"
    kafka = "kafka"
    celery = "celery"
    rabbitmq = "rabbitmq"
    influxdb = "influxdb"

    def get_scheme(self) -> str:
        return Schemes[self.value].value

    def create_url(self, data: dict[str, str | int]) -> str:
        __config = URLConfig(scheme=self.get_scheme(), **data)
        url: str = __config.get_human_url()
        logger.debug('Created URL service', url=url, service=self.value)

        return url
