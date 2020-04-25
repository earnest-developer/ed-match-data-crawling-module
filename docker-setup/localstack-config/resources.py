import json, logging, os
import boto3
from botocore.exceptions import ClientError
from time import sleep


def create_session(aws_access_key_id, aws_secret_access_key, aws_region):
    return boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )


def get_sqs_queue(sqs, queue_name):
    attempts = 0
    while attempts < 5:
        try:
            sleep(1)
            response = sqs.list_queues(
                QueueNamePrefix=queue_name
            )

            if "QueueUrls" in response:
                return next(iter(response['QueueUrls']), None)

            return None

        except ClientError:
            logging.info("Error listing queues")
            attempts += 1

    raise Exception('Could not connect to sqs')


def create_sqs_queue(sqs, queue_name, is_fifo):
    exists = get_sqs_queue(sqs, queue_name)

    if exists is not None:
        logging.info(f"SQS: The {queue_name} queue is already created")
        return

    queue = sqs.create_queue(
        QueueName=queue_name,
        Attributes={'FifoQueue': is_fifo, 'ContentBasedDeduplication': is_fifo}
    )

    logging.info(f"SQS: Created {queue_name} queue with URL: {queue['QueueUrl']}")
    return queue


def create_client(session, service, key_id, port):
    if key_id == 'xxx':
        endpoint = os.environ.get('ENDPOINT_URL', 'localhost')
        return session.client(service, endpoint_url=f'http://{endpoint}:{port}')

    return session.client(service)
