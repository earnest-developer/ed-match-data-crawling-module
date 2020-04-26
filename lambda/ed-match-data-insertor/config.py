#! python3
# config.py -- A wrapper for environmental variables

from os import environ

try:
    import config_local
except ModuleNotFoundError:
    config_local = None
else:
    print('Local configuration file loaded')

MATCH_DATA_NOTIFICATIONS_QUEUE_URL = config_local and config_local.MATCH_DATA_NOTIFICATIONS_QUEUE_URL or environ.get('MATCH_DATA_NOTIFICATIONS_QUEUE_URL')
MYSQL_CONNECTION_STRING = config_local and config_local.MYSQL_CONNECTION_STRING or environ.get('MYSQL_CONNECTION_STRING')
