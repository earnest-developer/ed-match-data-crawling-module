import logging, os
import resources as aws

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def main():
    key_id = os.environ.get('AWS_SECRET_KEY_ID', 'xxx')
    session = aws.create_session(
        key_id,
        os.environ.get('AWS_SECRET_ACCESS_KEY', 'xxx'),
        os.environ.get('REGION_NAME', 'eu-west-2')
    )

    # Create SQS queues
    sqs = aws.create_client(session, 'sqs', key_id, '4576')
    aws.create_sqs_queue(sqs, 'ed-match-data-crawling-module-xxc-crawler-jobs', 'false')
    aws.create_sqs_queue(sqs, 'ed-match-data-crawling-module-ingest.fifo', 'true')
    aws.create_sqs_queue(sqs, 'ed-match-data-notifications', 'false')
