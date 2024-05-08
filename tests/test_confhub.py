from confhub.models import URLConfig
from confhub.reader import ReaderConf


def test_model() -> None:
    url_config = URLConfig(
        scheme='http',
        port=8080
    )

    assert url_config.scheme == 'http'
    assert url_config.port == 8080


def test_reader() -> None:
    reader = ReaderConf('tests/settings.yml', 'tests/.secrets.yml', dev=True, )
    reader.create_service_urls()
    configuration = reader.data

    assert configuration.get('postgresql_url') == 'postgresql+asyncpg://ghost:qwerty@127.0.0.1:5432/database'
