POSTGRESQL_CONFIG = {
    'user': "test",
    'password': "test123",
    'host': "postgres",
    'dbname': "postgres",
    'port': 5432
}

POSTGRESQL_CONNECT_CFG = {
    'host': POSTGRESQL_CONFIG.get('host'),
    'port': POSTGRESQL_CONFIG.get('port'),
    'dbname': POSTGRESQL_CONFIG.get('dbname')
}

POSTGRESQL_LOGIN_AUTH_CFG = {
    'password': POSTGRESQL_CONFIG.get('password'),
    'user': POSTGRESQL_CONFIG.get('user')
}

MYSQL_CONFIG = {
    'user': "root",
    'password': "toor",
    'host': "mysql",
    'dbname': "test",
    'port': 3306
}

MYSQL_CONNECT_CFG = {
    'host': MYSQL_CONFIG.get('host'),
    'port': MYSQL_CONFIG.get('port'),
    'dbname': MYSQL_CONFIG.get('dbname')
}

MYSQL_LOGIN_AUTH_CFG = {
    'password': MYSQL_CONFIG.get('password'),
    'user': MYSQL_CONFIG.get('user')
}
