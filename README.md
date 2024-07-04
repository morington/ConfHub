# ConfHub

**Данный модуль позволяет загружать и обрабатывать конфигурационные файлы различных форматов:**
- `.toml`
- `.yaml`
- `.json`
- `.ini`
- `.py`
- `.env`

### !! В конфигурации определена настройка логов с помощью `structlog` и моей настройки процессоров !!

# Основные возможности:

- *Парсинг файлов конфигурации и объединение данных в единый словарь*
- *Автоматическое создание URL-адресов для сервисов по их настройкам*
- *Поддержка работы с переменными окружения (.env файлы)*
- *Возможность задания приоритетных настроек для разработки*
- *Использование модуля позволяет упростить доступ к конфигурационным данным в коде проекта, а также автоматизировать ряд рутинных задач, связанных с конфигурацией.*

# Установка

```console
pip install confhub
```

# Использование

Вы можете автоматически сгенерировать файлы конфигурации в удобное место:

```console
confhub --create config
```

*confhub -c/--create **название_вашей папки***

Для генерации файлов в текущую папку используйте точку:

```console
confhub -c .
```

Если папки не существует, confhub запросит у пользователя подтверждение о создание папки:

```console
confhub -c test

Do you want to create a new folder at (D:\ConfHub\test)? [Y/n]
: y
2024-05-08 13:00:38 [info     ] Loading configuration files    [commands.py:generate_configurations_files:32] secret_file=WindowsPath('D:/ConfHub/test/.secrets.yml') secret_file__example=WindowsPath('D:/ConfHub/test/example__secrets.yml') settings=WindowsPath('D:/ConfHub/test/settings.yml')
```

Далее вы можете использовать конфигурацию в вашем коде:

```python
from confhub.reader import ReaderConf

reader = ReaderConf('config/settings.yml', 'config/.secrets.yml', dev=True)
reader.create_service_urls()
configuration = reader.models

assert configuration.get('postgresql_url') == 'postgresql+asyncpg://ghost:qwerty@127.0.0.1:5432/database'
# True
```

По умолчанию используется глобальная конфигурация для логирования с режимом DEBUG:

```python
from confhub.setup_logger import LoggerReg

logger_registrations = [
    LoggerReg(name="", level=LoggerReg.Level.DEBUG)
]
```

Чтобы изменить ее передайте в параметр ReaderConf ваши настройки:

```python
from confhub.reader import ReaderConf
from confhub.setup_logger import LoggerReg
"""
    class Level(Enum):
        DEBUG: str = "DEBUG"
        INFO: str = "INFO"
        WARNING: str = "WARNING"
        ERROR: str = "ERROR"
        CRITICAL: str = "CRITICAL"
        NONE: str = None
"""

reader = ReaderConf(
    'config/settings.yml', 'config/.secrets.yml', dev=True,
    logger_registrations = [
        LoggerReg(name="название вашего логера", level=LoggerReg.Level.INFO),
        LoggerReg(name="название вашего следующего логера", level=LoggerReg.Level.ERROR),
        # и так далее
    ]
)
```

## Внимание!

Настройки логирования с записью в файл пока на экспериментальном уровне. Пожалуйста, сообщайте о всех багах мне в [личку телеграм](https://t.me/morington).
