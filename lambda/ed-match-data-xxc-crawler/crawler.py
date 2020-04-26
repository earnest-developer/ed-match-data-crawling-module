#! python3
# crawler.py -- The crawling module for XXC Sports

import requests
import bs4
import logging
import config
from datetime import date
from dateutil import parser
from multiprocessing import Process, Pipe

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def map_url(crawling_date: date, starting_date: date, url_division: str):
    """Returns the parent page URL based on the arguments provided

    :param crawling_date: The day the URL should be updated to
    :param starting_date: The day crawling commenced
    :param url_division: The football division in the URL

    """

    if(crawling_date > date.today()):
        raise ValueError('Cannot map a URL from a future datetime')

    year_month_suffix = str(crawling_date.year) + '-' + str(crawling_date.month).rjust(2, '0')

    if(crawling_date == date.today() and starting_date != date.today()):
        year_month_suffix = year_month_suffix + '?filter=results'

    # https://www.xxx.xx.xx/sport/football/xxx/scores-fixtures/2020-05
    return config.BASE_CRAWL_URL + '/sport/football/' + url_division + '/scores-fixtures/' + year_month_suffix


def get_match_blocks(url: str):
    """Returns a list of match day blocks listing football matches"""

    logging.info('Crawling: %s', url)

    parent_page_response = requests.get(url)
    parent_page_response.raise_for_status()

    monthly_fixtures_response_soup = bs4.BeautifulSoup(parent_page_response.text, features="html.parser")
    match_blocks = monthly_fixtures_response_soup.find_all("div", class_="qa-match-block")

    return match_blocks


def get_match_data(match_block):
    """Accepts a block listing a day's matches. Initiates a scrape process and returns a list of results"""

    match_block_item = match_block.find_all("li", class_="gs-o-list-ui__item")
    match_block_not_ft = [match_link for match_link in match_block_item if not match_link.text.endswith('FT')]

    [logging.warning('Omitting: %s', match_link.text) for match_link in match_block_not_ft]

    match_block_anchors = match_block.find_all("a", class_="sp-c-fixture__block-link")
    match_block_ft = [match_link for match_link in match_block_anchors if match_link.text.endswith('FT')]
    match_block_links = [match_link.attrs.get("href") for match_link in match_block_ft]
    match_data: [MatchData] = scrape_data_from_pages(match_block_links)

    return match_data


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

    match_date = single_match_response_soup.find("time", class_="fixture__date gel-minion").text
    parsed_date = parser.parse(match_date)
    match_date_formatted = parsed_date.strftime('%Y-%m-%d')

    home_team = single_match_response_soup.find("span", class_="fixture__team-name--home").text
    away_team = single_match_response_soup.find("span", class_="fixture__team-name--away").text

    ft_hg = single_match_response_soup.find("span", class_="fixture__number fixture__number--home fixture__number--ft").text
    ft_ag = single_match_response_soup.find("span", class_="fixture__number fixture__number--away fixture__number--ft").text

    ft_r = map_result_from_score(ft_hg, ft_ag)

    half_time_text = single_match_response_soup.find("span", class_="fixture__status gel-brevier").text
    ht_hg = half_time_text.split('-')[0].split(' ')[1]
    ht_ag = half_time_text.split('-')[1]

    ht_r = map_result_from_score(ht_hg, ht_ag)

    result = MatchData("E0", match_date_formatted, home_team, away_team, ft_hg, ft_ag, ft_r, ht_hg, ht_ag, ht_r, "season")

    pipe_connection.send([result])
    pipe_connection.close()


def map_result_from_score(home_score: int, away_score: int):
    """Returns a letter indicating the result (Draw, Home, Away)"""\

    if home_score == away_score:
        return 'D'
    if home_score > away_score:
        return 'H'
    else:
        return 'A'


class MatchData:
    """Result class holding all scraped football match data"""

    def __init__(self, division, match_date, home_team, away_team, ft_hg, ft_ag, ft_r, ht_hg, ht_ag, ht_r, season):

        if not division:
            raise ValueError('division must have a value')
        if not match_date:
            raise ValueError('match_date must have a value')
        if not home_team:
            raise ValueError('home_team must have a value')
        if not away_team:
            raise ValueError('away_team must have a value')
        if not ft_hg:
            raise ValueError('ft_hg must have a value')
        if not ft_ag:
            raise ValueError('ft_ag must have a value')
        if not ft_r:
            raise ValueError('ft_r must have a value')
        if not ht_hg:
            raise ValueError('ht_hg must have a value')
        if not ht_ag:
            raise ValueError('ht_ag must have a value')
        if not ht_r:
            raise ValueError('ht_r must have a value')
        if not season:
            raise ValueError('season must have a value')

        self.division = division
        self.match_date = match_date
        self.home_team = home_team
        self.away_team = away_team
        self.ft_hg = ft_hg
        self.ft_ag = ft_ag
        self.ft_r = ft_r
        self.ht_hg = ht_hg
        self.ht_ag = ht_ag
        self.ht_r = ht_r
        self.season = season
