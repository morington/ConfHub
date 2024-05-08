SECRETS = """dynaconf_merge: True

development:
  # Development Configuration
  
  postgresql:
    port: 5432
    user: 'ghost'
    password: 'qwerty'
    path: 'database'

release:
  # Release configuration
  
  postgresql:
    port: 0000
    user: ''
    password: ''
    path: ''
"""

SECRETS_EXAMPLE = """dynaconf_merge: True

development:
  # Development Configuration
  
  postgresql:
    port: <port :number>
    user: <username :string>
    password: <password :string>
    path: <name_database :string>

release:
  # Release configuration
  
  postgresql:
    port: <port :number>
    user: <username :string>
    password: <password :string>
    path: <name_database :string>
"""

SETTINGS = """dynaconf_merge: True

development:
  # Development Configuration
  
  postgresql:
    host: '127.0.0.1'

release:
  # Release configuration
  
  postgresql:
    host: '0.0.0.0'
"""


