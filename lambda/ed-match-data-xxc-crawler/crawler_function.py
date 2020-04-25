#! python3
# crawler.py -- A stateless crawler for scrapping historic football match data

import boto3
import requests
import bs4
import json
import utils
import config
from multiprocessing import Process, Pipe
from datetime import date
from dateutil import relativedelta, parser
from botocore.exceptions import ClientError


sqs_client = boto3.client('sqs')


def lambda_handler(event, context):

    message = parse_message(event)

    starting_date: str = date.fromisoformat(message['starting_date'].split("T")[0])
    url_division: str = message['division']

    crawl_date = starting_date

    while crawl_date <= date.today():

        parent_url = utils.map_parent_url(crawl_date, starting_date, url_division)

        print('Crawling: ' + parent_url)

        parent_page_response = requests.get(parent_url)
        parent_page_response.raise_for_status()

        monthly_fixtures_response_soup = bs4.BeautifulSoup(parent_page_response.text, features="html.parser")
        match_blocks = monthly_fixtures_response_soup.find_all("div", class_="qa-match-block")

        for match_block in reversed(match_blocks):

            match_block_date = match_block.find("h3", class_="sp-c-match-list-heading").text

            match_block_item = match_block.find_all("li", class_="gs-o-list-ui__item")
            match_block_not_ft = [match_link for match_link in match_block_item if not match_link.text.endswith('FT')]
            [print('Omitting: ' + match_link.text) for match_link in match_block_not_ft]

            match_block_anchors = match_block.find_all("a", class_="sp-c-fixture__block-link")
            match_block_ft = [match_link for match_link in match_block_anchors if match_link.text.endswith('FT')]
            match_block_links = [match_link.attrs.get("href") for match_link in match_block_ft]
            match_data = scrape_data_from_pages(match_block_links)

            if(match_data):
                queue_match_data(match_block_date, match_data)

        # Progress the crawl
        crawl_date += relativedelta(months=1)

    print('Crawl accomplished')


def scrape_data_from_pages(match_page_links: list):
    """Creates new processes to scrape the page data under the provided URIs

    :param match_page_links: A list of page URIs

    """

    # create a list to keep all processes
    processes = []
    # create a list to keep connections
    parent_connections = []

    # create a process per match_page_link
    for match_page_link in match_page_links:
        # create a duplex pipe for communication
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)

        # create the process, pass instance and connection
        process = Process(target=scrape_match_page_data, args=(match_page_link, child_conn, ))
        processes.append(process)

    # start all processes
    for process in processes:
        process.start()

    # make sure that all processes have finished
    for process in processes:
        process.join()

    return [parent_connection.recv()[0] for parent_connection in parent_connections]


def scrape_match_page_data(page_uri: str, pipe_connection: Pipe):
    """Scrapes the details page for match data. Returns a MatchData object wrapping the results. Calls are parallelized

    :param page_uri: The page URI
    :param pipe_connection: The pipe connection used to send data to the caller of this function

    """

    url = config.BASE_CRAWL_URL + page_uri  # https://www.xxx.xx.xx/sport/football/51595063

    single_match_response = requests.get(url)
    single_match_response.raise_for_status()

    single_match_response_soup = bs4.BeautifulSoup(single_match_response.text, features="html.parser")

    home_team = single_match_response_soup.find("span", class_="fixture__team-name--home").text
    away_team = single_match_response_soup.find("span", class_="fixture__team-name--away").text

    ft_hg = single_match_response_soup.find("span", class_="fixture__number fixture__number--home fixture__number--ft").text
    ft_ag = single_match_response_soup.find("span", class_="fixture__number fixture__number--away fixture__number--ft").text

    ft_r = utils.map_ft_r_from_score(ft_hg, ft_ag)

    result = utils.MatchData(home_team, away_team, ft_hg, ft_ag, ft_r)

    pipe_connection.send([result])
    pipe_connection.close()


def queue_match_data(match_block_date: str, match_data: list):
    """Sends the match data to the ingest SQS queue. Orders them so they have an expected hash

    :param match_block_date: The page URI
    :param match_data: The pipe connection used to send data to the caller of this function

    """

    match_date = parser.parse(match_block_date).strftime('%Y-%m-%d')

    match_data.sort(key=lambda x: x.home_team, reverse=False)
    serialized_message = json.dumps(match_data, default=utils.obj_dict)

    try:
        sqs_client.send_message(
            QueueUrl=config.MATCH_DATA_INGEST_QUEUE_URL,
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
            MessageGroupId='xxc-crawler'
        )

    except ClientError as exception:
        print(exception)

    print('Queuing ' + match_date + ' for ingestion')


def parse_message(event):
    message_body = event['Records'][0]['body']
    print('Dequeuing message: ' + message_body)
    return json.loads(message_body)
