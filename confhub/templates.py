SERVICE = """developer_mode: True
models_path: {models_path}
configs_path: {configs_path}

"""

SAMPLE_MODELS = """from confhub import BlockCore, field

''' Sample class based on configuration for PostgreSQL '''


class PostgreSQL(BlockCore):
    __block__ = 'postgresql'  # Name of the block header in the configuration

    '''
    Creating values is very simple:
        value_name = field(data_type, development_mode=True/False, secret=True/False, filename='MY_FILE')
        
        data_type - типа значения данных в конфигурации, поддерживаемые типы: 
        development_mode - indicates whether the field will have a different value in development mode (default False)
        secret - means whether to hide this field as secrets (default is False, all files go to settings by default)
        filename - you can independently define the field in the file that is required, Confhub will create it for you
    '''
    scheme = field(str)
    host = field(str, development_mode=True)
    port = field(int, secret=True)
    user = field(str, secret=True)
    password = field(str, secret=True)
    path = field(str, secret=True)

"""

INIT_SAMPLE = """
__all__ = []

"""
