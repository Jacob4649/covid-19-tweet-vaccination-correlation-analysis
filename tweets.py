"""
Represents and filters tweets about the COVID vaccines,
and their rollout across the united states
"""

from __future__ import annotations
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import csv
from datetime import datetime
from typing import Iterable, List, Optional
from nltk.sentiment import SentimentIntensityAnalyzer
from locations import Location
import states


class Tweet(object):
    """
    Class representing a single tweet made about COVID
    vaccination

    Attributes:
        - user: The handle of the user who tweeted this
        - followers: The number of followers the tweeting user has
        - tweet: The content of the tweet
        - time_stamp: The time the tweet was tweeted
        - location: State from which the tweet was tweeted
        - raw_location: Raw location string the user included
        - polarity: Compound result of VADER sentiment analysis of this tweet

    Representation Invariants:
        - followers >= 0
    """

    user: str
    followers: int
    tweet: str
    time_stamp: datetime
    location: Location
    raw_location: str
    polarity: float

    def __init__(self, row: List[str], analyzer: SentimentIntensityAnalyzer):
        """Create a tweet from a
        row in a csv of tweets, and a sentiment analyzer to use
        to analyze the tweet content

        Preconditions:
            - len(row) == 13
        """
        self.user = row[0]
        self.tweet = row[9]
        self.location = states.location_lookup(row[1])
        self.followers = int(float(row[4]))
        self.time_stamp = _from_csv_date(row[8])
        self.raw_location = row[1]
        scores = analyzer.polarity_scores(self.tweet)
        self.polarity = scores['compound']


def from_csv(path: str, analyzer: SentimentIntensityAnalyzer) -> Iterable[Tweet]:
    """Return a generator for tweets from a csv file.

    Yields only tweets determined to match the selection
    criteria for this project.

    Uses provided sentiment intensity analyzer to compute vader polarities"""
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Skip header

        # filter out unwanted rows
        filtered_rows = filter(_filter_row, reader)

        def create_tweet(row: List[str]) -> Tweet:
            """Return a tweet created from a csv row
            
            Function for use with map that creates a
            tweet from a csv row"""
            return Tweet(row, analyzer)

        with ThreadPoolExecutor(max_workers=10) as reader_executor:
            # disk io, object initialization, and vader polarity assignment
            for result in reader_executor.map(create_tweet, filtered_rows):
                yield result


def _filter_row(row: List[str]) -> bool:
    """Return whether a row representing a tweet from a csv
    matches the selection criteria for this project

    Specifically matches the following conditions:
        - Follower information is intact
        - Contains a valid date
        - Location contains a US state code or US state name

    Preconditions:
        - len(row) == 13"""
    return len(row) == 13 and row[4] != '' and _from_csv_date(row[8]) is not None \
        and states.location_lookup(row[1]) is not None


def _from_csv_date(date: str) -> Optional[datetime]:
    """Return a date from the csv converted to a datetime,
    or None if date cannot be converted.

    Necessary because dates in the csv are stored in multiple
    formats"""
    try:
        return datetime.strptime(date, '%Y-%m-%d %H:%M')
    except ValueError:
        pass
    try:
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    try:
        return datetime.strptime(date, '%d-%m-%Y %H:%M')
    except ValueError:
        pass
    try:
        return datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
    except ValueError:
        pass


if __name__ == '__main__':
    import os.path
    UNFILTERED_PATH = '/home/jacob/Downloads/covidvaccine.csv'
    #'C:\\Users\\Jacob\\Downloads\\archive\\covidvaccine.csv'
    FILTERED_PATH = 'C:\\Users\\Jacob\\Downloads\\archive\\filtered.csv'

    ANALYZER = SentimentIntensityAnalyzer()

    # if not os.path.isfile(FILTERED_PATH):
    #     filter_and_save(UNFILTERED_PATH, FILTERED_PATH, ANALYZER)

    tweets = from_csv(UNFILTERED_PATH, ANALYZER)

    locations = {}

    for item in tweets:
        if item.location.code in locations:
            t = locations[item.location.code]
            polarity, num = t
            polarity = polarity * num + item.polarity
            num += 1
            polarity /= num
            locations[item.location.code] = (polarity, num)
        else:
            locations[item.location.code] = (item.polarity, 1)

    for row in sorted([(l, locations[l])
                       for l in locations], key=lambda a: a[1][0], reverse=True):
        print(f'{states.code_lookup(row[0]).name}: {row[1][0]}')
