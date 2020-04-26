#! python3
# function.py -- A stateless service that inserts data in the database and queues notifications

import boto3
import config
import json
import logging
import mysql_client

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

sqs_client = boto3.client('sqs')
sql_connection = mysql_client.create_connection(config.MYSQL_CONNECTION_STRING)

query = """INSERT INTO football_match_data (division, match_date, home_team, away_team, ft_hg, ft_ag, ft_r, ht_hg, ht_ag, ht_r, season)
                        VALUES (%(division)s, %(match_date)s, %(home_team)s, %(away_team)s,
                                %(ft_hg)s, %(ft_ag)s, %(ft_r)s, %(ht_hg)s, %(ht_ag)s, %(ht_r)s, %(season)s) """


def lambda_handler(event, context):

    (date, match_block) = parse_message(event)

    logging.info('Handling batch %s', date)

    for match in match_block:

        affected_rows = mysql_client.execute_query(sql_connection, query, match)

        if(affected_rows):
            queue_notification(match['home_team'], match['away_team'], match['match_date'])
        else:
            logging.warning('Pair %s:%s from %s failed to insert %s', match['home_team'], match['away_team'], match['match_date'])

    logging.info('Handled batch %s', date)


def queue_notification(home_team: str, away_team: str, match_date: str):
    """Sends the match data to the ingest SQS queue. Orders them so they have an expected hash"""

    serialized_message = json.dumps((home_team, away_team, match_date))

    sqs_client.send_message(
        QueueUrl=config.MATCH_DATA_NOTIFICATIONS_QUEUE_URL,
        MessageAttributes={
            'MessageType': {
                'DataType': 'String',
                'StringValue': 'MatchDataNotification'
            }
        },
        MessageBody=serialized_message
    )


def parse_message(event):
    match_date = event['Records'][0]['messageAttributes']['MatchDate']['stringValue']
    message_body = event['Records'][0]['body']
    logging.info('Dequeuing batch: ' + match_date)
    return (match_date, json.loads(message_body))
