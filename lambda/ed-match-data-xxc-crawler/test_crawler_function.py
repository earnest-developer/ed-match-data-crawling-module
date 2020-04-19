import pytest
import json
import crawler_function


@pytest.fixture()
def sqs_crawl_job_event():
    """ Loads the event file in JSON """

    with open('../ed-match-data-crawling-module/events/sqs-new-crawl-job.json', 'r') as event_file:
        event_data = event_file.read()

    return json.loads(event_data)


def test_lambda_handler(sqs_crawl_job_event):
    """ Loads the event file in JSON """

    # Setup
    # TODO: Mock the SQS Call

    # Act
    crawler_function.lambda_handler(sqs_crawl_job_event, "")

    # Assert
    assert 1 == 1
