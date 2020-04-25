import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import setup_dependencies


def check_localstack(endpoint):
    session = requests.Session()
    retry = Retry(total=10, backoff_factor=0.05)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    endpoint = os.environ.get('ENDPOINT_URL', 'localhost')
    session.get(f'http://{endpoint}:8080')


if __name__ == "__main__":
    endpoint = os.environ.get('ENDPOINT_URL', 'localhost')
    check_localstack(endpoint)

    setup_dependencies.main()
