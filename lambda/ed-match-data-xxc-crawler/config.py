#! python3
# config.py -- A wrapper for environmental variables

from os import environ

try:
    import config_local
except ModuleNotFoundError:
    config_local = None
else:
    print('Local configuration file loaded')

# BASE_CRAWL_URL = config_local and config_local.BASE_CRAWL_URL or environ.get('BASE_CRAWL_URL')
# JOB_QUEUE_URL = config_local and config_local.JOB_QUEUE_URL or environ.get('JOB_QUEUE_URL')
# INSERTOR_INGEST_QUEUE_URL = config_local and config_local.INSERTOR_INGEST_QUEUE_URL or environ.get('INSERTOR_INGEST_QUEUE_URL')

BASE_CRAWL_URL = environ.get('BASE_CRAWL_URL')
JOB_QUEUE_URL = environ.get('JOB_QUEUE_URL')
INSERTOR_INGEST_QUEUE_URL = environ.get('INSERTOR_INGEST_QUEUE_URL')
