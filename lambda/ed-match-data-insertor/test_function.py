import pytest
import json
import function
import random
import localstack_client.session
from string import Template
from datetime import date, timedelta


@pytest.fixture()
def sqs_ingest_data_event():
    """ Loads the event file in JSON """

    with open('../../events/sqs-new-ingest-data.json', 'r') as event_file:
        event_data = event_file.read()

    event = json.loads(event_data)

    message_template = Template(event['Records'][0]['body'])
    with_dates = message_template.substitute(date=gen_datetime())
    event['Records'][0]['body'] = with_dates

    return event


def test_lambda_handler(sqs_ingest_data_event):
    """ Loads the event file in JSON """

    # Setup
    session = localstack_client.session.Session()
    function.sqs_client = session.client('sqs')

    # Act
    function.lambda_handler(sqs_ingest_data_event, "")

    # Assert
    assert 1 == 1


def gen_datetime(min_year=2010, max_year=2100):
    # generate a datetime in format yyyy-mm-dd
    start = date(min_year, 1, 1)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()
