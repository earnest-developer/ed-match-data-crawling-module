#! python3
# utils.py -- Utility functions and types

import config
from datetime import date


# Classes
class MatchData:

    def __init__(self, home_team, away_team, ft_hg, ft_ag, ft_r):
        self.home_team = home_team
        self.away_team = away_team
        self.ft_hg = ft_hg
        self.ft_ag = ft_ag
        self.ft_r = ft_r

    def __str__(self):
        return '%s:%s:%s:%s:%s' % (self.home_team, self.away_team, self.ft_hg, self.ft_ag, self.ft_r)


# Functions
def map_parent_url(crawling_date: date, starting_date: date, url_division: str):
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


def map_ft_r_from_score(ft_hg: int, ft_ag: int):
    """Returns a letter indicating the full time match result (Draw, Home, Away)

    :param ft_hg: The full time Home Team score
    :param ft_ag: The full time Away Team score

    """
    if ft_hg == ft_ag:
        return 'D'
    if ft_hg > ft_ag:
        return 'H'
    else:
        return 'A'


def obj_dict(obj):
    return obj.__dict__
