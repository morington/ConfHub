SECRETS = """dynaconf_merge: '@bool True'

development:
  # Development Configuration
  
  postgresql:
    scheme: '@str postgresql+asyncpg'
    port: '@int 5432'
    user: '@str ghost'
    password: '@str qwerty'
    path: '@str database'

release:
  # Release configuration
  
  postgresql:
    scheme: '@str postgresql+asyncpg'
    port: '@int 0000'
    user: '@str '
    password: '@str '
    path: '@str '

"""

SECRETS_EXAMPLE = """dynaconf_merge: '@bool True'

development:
  # Development Configuration
  
  postgresql:
    port: '@int '
    user: '@str '
    password: '@str '
    path: '@str '

release:
  # Release configuration
  
  postgresql:
    port: '@int '
    user: '@str '
    password: '@str '
    path: '@str '

"""

SETTINGS = """dynaconf_merge: '@bool True'
DEV: '@bool True'

development:
  # Development Configuration
  
  postgresql:
    host: '@str 127.0.0.1'

release:
  # Release configuration
  
  postgresql:
    host: '@str 0.0.0.0'
"""


