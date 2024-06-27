![](./logo.png)

<p align="center">
    <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/confhub">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/confhub">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/confhub">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/confhub">
</p>

*********
## About
<b>Сonfhub</b> is a library that relieves developers of the tedious task of creating and managing configuration files. Instead of wasting valuable time writing configurations, developers can focus on building the site's functionality.

### History
Based on our own experience and the experience of our colleagues, we realized that the process of working with configurations had become a real burden. We wanted something simple and effective. After several weeks of testing our MVP, we identified the strengths and weaknesses and presented the first alpha version of confhub to the world. Despite its shortcomings, it showed prospects for development.

### Updated version (>= 0.1.0.5a)
We currently offer a significantly improved version of confhub, which has extensive functionality. You can now dynamically generate configurations from model classes, greatly simplifying the process. In addition, the library supports developer mode, which speeds up the process of replacing configurations several times.

*********
## Documentation

### Getting started with confhub

*********
**Installation and initialization**

To get started with confhub, you need to create a project and install the Python virtual environment. Then install the confhub library into the virtual environment.

```bash
pip install confhub
```

After installing the library, initialize it in your project with the following command:

```bash
confhub init <folder>
```

Where `<folder>` is the name of the folder where the entire configuration structure will be placed. For example:

```bash
confhub init configurations
```

This command will create the following structure in the root of your project:

- `.service.yml`: Contains basic settings such as paths to configs and models. The file is automatically added to `.gitignore`.
- `configurations/`: A folder created at your request.
  - `config/`: A folder to store the generated configuration files.
  - `models.py`: A file for describing models. Initially contains an example PostgreSQL model.

*********
**Creating Models**

In `models.py` you can describe your models. For example:

```python
from confhub import BlockCore, field

class PostgreSQL(BlockCore):
    __block__ = 'postgresql'

    scheme = field(str)
    host = field(str, development_mode=True)
    port = field(int, secret=True)
    user = field(str, secret=True)
    password = field(str, secret=True)
    path = field(str, secret=True)

class ItemBlock(BlockCore):
    __block__ = 'item_block'

    item_name = field(str)

class TestBlock(BlockCore):
    __block__ = 'test_block'

    item_block = ItemBlock()
    illuminati = field(str, filename='illuminati')
    admins = field(str)
```

*********
**Generation of configuration files**

After creating models, you can generate configuration files using the command:

```bash
confhub generate_models
```

This command converts your models into configuration files with a `.yml` extension.

Confhub generates two main files: `settings` and `.secrets`. The secrets are automatically added to `.gitignore`. You can also specify `filename` in models to create additional files in the `config` folder.

__Do not use `secrets` and `filename` at the same time. There may be unexpected consequences at this point!__

This documentation will help you get started with confhub and use its features to simplify the process of working with configurations in your project.

*********
**Filling configurations**

Fill in the configurations, e.g:

```yaml
postgresql:
  password: str; qwer
  path: str; db_confhub
  port: int; 5432
  user: str; morington
```

The data type is specified before the value. Available types: `str`, `int`, `bool`, `float`. YML also supports lists, in models we prescribe a type for the value of each element in a list, and with YML we make a list:

```yaml
admins:
  - str; Adam
  - str; John
  - str; Saly
```

*********
**Read configurations**

To read configurations, use the following code:

```python
import structlog
from confhub import Confhub
from confhub.setup_logger import LoggerReg

logger = structlog.get_logger(__name__)

if __name__ == '__main__':
    config = Confhub(developer_mode=True, logger_regs=[
        LoggerReg(name="", level=LoggerReg.Level.DEBUG,)
    ]).data

    logger.info("PostgreSQL", host=config.postgresql.host)
    logger.info("Admins", host=config.test.admins)
```

*********
**Logging Configuration**

Sonfhub uses `structlog` for logging. You can configure loggers using ``LoggerReg``:

```python
LoggerReg(name="", level=LoggerReg.Level.DEBUG)
```

*********
**developer_mode**

The `developer_mode` argument is available both in the `Confhub` class and in the `.service.yml` file. The class argument takes precedence over the file.

*********
## Main developers

### [Adam Morington](https://github.com/morington)

*********
## License
[Сonfhub](https://github.com/morington/confhub) is distributed under the [MIT license](https://github.com/morington/confhub/blob/main/LICENSE). This means that you are free to use, modify and distribute the library for any purpose, including commercial use.