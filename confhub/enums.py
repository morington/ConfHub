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

        __hidden_config = __config
        __hidden_config.user = f"{__hidden_config.user[0]}{'*'*len(__hidden_config.user)}{__hidden_config.user[-1]}"
        __hidden_config.password = '*' * len(__hidden_config.password)
        __hidden_url = __hidden_config.get_human_url()

        logger.debug('Created URL service', url=__hidden_url, service=self.value)

        return url
