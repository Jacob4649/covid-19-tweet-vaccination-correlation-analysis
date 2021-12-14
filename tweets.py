"""
Tweets

Module Description
==================
Represents and filters tweets about the COVID vaccines,
and their rollout across the united states

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Jacob Klimczak, Ryan Merheby and Sean Ryan.
"""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import csv
import datetime
from typing import Iterable, List, Optional
from app import App
from locations import Location


class Tweet:
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
    time_stamp: datetime.datetime
    location: Location
    raw_location: str
    polarity: float

    def __init__(self, row: List[str], app: App) -> None:
        """Create a tweet from a
        row in a csv of tweets and an app state bundle class

        Preconditions:
            - len(row) == 13
        """
        self.user = row[0]
        self.tweet = row[9]
        self.location = app.location_lookup(row[1])
        self.followers = int(float(row[4]))
        self.time_stamp = _from_csv_date(row[8])
        self.raw_location = row[1]
        scores = app.analyzer.polarity_scores(self.tweet)
        self.polarity = scores['compound']


def from_csv(path: str, app: App) -> Iterable[Tweet]:
    """Return a generator for tweets from a csv file.

    Yields only tweets determined to match the selection
    criteria for this project.

    Uses provided app's sentiment intensity analyzer to compute vader polarities"""
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Skip header

        def tweet_filter(row: List[str]) -> bool:
            """Return a boolean indicating whether a specified row is suitable
            to use to generate a tweet object

            Function for use with filter"""
            return _filter_row(row, app)

        # filter out unwanted rows
        filtered_rows = filter(tweet_filter, reader)

        def create_tweet(row: List[str]) -> Tweet:
            """Return a tweet created from a csv row

            Function for use with map that creates a
            tweet from a csv row"""
            return Tweet(row, app)

        with ThreadPoolExecutor(max_workers=10) as reader_executor:
            # disk io, object initialization, and vader polarity assignment
            for result in reader_executor.map(create_tweet, filtered_rows):
                yield result


def _filter_row(row: List[str], app: App) -> bool:
    """Return whether a row representing a tweet from a csv
    matches the selection criteria for this project, using the row
    and an app state bundle

    Specifically matches the following conditions:
        - Has correct number of columns
        - Follower information is intact
        - Contains a valid date
        - Location contains a US state code or US state name"""
    return len(row) == 13 and row[4] != '' and _from_csv_date(row[8]) is not None \
        and app.location_lookup(row[1]) is not None


def _from_csv_date(date: str) -> Optional[datetime.datetime]:
    """Return a date from the csv converted to a datetime,
    or None if date cannot be converted.

    Necessary because dates in the csv are stored in multiple
    formats"""
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(date, '%d-%m-%Y %H:%M')
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
    except ValueError:
        pass
    return None


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': ['concurrent.futures',
                          'csv',
                          'datetime',
                          'nltk.sentiment',
                          'app',
                          'locations',
                          'typing'],
        'allowed-io': ['from_csv'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })
