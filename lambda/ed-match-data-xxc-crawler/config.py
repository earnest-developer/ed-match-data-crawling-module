#! python3
# config.py -- A wrapper for environmental variables

from os import environ

BASE_CRAWL_URL = environ.get('BASE_CRAWL_URL')
JOB_QUEUE_URL = environ.get('JOB_QUEUE_URL')
MATCH_DATA_INGEST_QUEUE_URL = environ.get('MATCH_DATA_INGEST_QUEUE_URL')
