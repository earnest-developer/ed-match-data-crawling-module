#! python3
# function.py -- A stateless crawler for scrapping historic football match data

import boto3
import json
import crawler
import config
import logging
from datetime import date
from dateutil import relativedelta


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
sqs_client = boto3.client('sqs')


def lambda_handler(event, context):

    (starting_date, url_division) = parse_message(event)

    crawl_date = starting_date

    while crawl_date <= date.today():

        monthly_scores_url = crawler.map_url(crawl_date, starting_date, url_division)

        match_blocks = crawler.get_match_blocks(monthly_scores_url)

        for match_block in reversed(match_blocks):

            match_data = crawler.get_match_data(match_block)

            if(match_data):
                queue_match_data(match_data)

        # Progress the crawl
        crawl_date += relativedelta.relativedelta(months=+1)

    logging.info('Crawl accomplished')


def queue_match_data(match_data: list):
    """Sends the match data to the ingest SQS queue. Orders them so they have an expected hash

    :param match_block_date: The date the maches occurred on
    :param match_data: The match data

    """

    match_date = match_data[0].match_date

    match_data.sort(key=lambda x: x.home_team, reverse=False)
    serialized_message = json.dumps(match_data, default=obj_dict)

    sqs_client.send_message(
        QueueUrl=config.INSERTOR_INGEST_QUEUE_URL,
        MessageAttributes={
            'MessageType': {
                'DataType': 'String',
                'StringValue': 'MatchData'
            },
            'MatchDate': {
                'DataType': 'String',
                'StringValue': match_date
            }
        },
        MessageBody=serialized_message,
        MessageGroupId='crawler-xxc'
    )

    logging.info(f'Queuing {match_date} for ingestion')


def parse_message(event):
    message_body = event['Records'][0]['body']
    logging.info('Dequeuing message: %s', message_body)
    message_body_json = json.loads(message_body)
    starting_date = date.fromisoformat(message_body_json['starting_date'].split("T")[0])
    url_division = message_body_json['division']
    return (starting_date, url_division)


def obj_dict(obj):
    return obj.__dict__
