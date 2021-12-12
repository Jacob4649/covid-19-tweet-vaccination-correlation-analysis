"""
Represents and filters tweets about the COVID vaccines,
and their rollout across the united states
"""

from __future__ import annotations
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
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

    def __init__(self, row: List[str], filtered=False):
        """Create a tweet from a
        row in a csv of tweets.

        The filtered flag indicates whether to skip checking
        the validity of inputs, and just assume they are
        correctly formatted

        Preconditions:
            - len(row) == 13
        """
        self.user = row[0]
        self.tweet = row[9]

        if filtered:
            self.location = states.code_lookup(row[1])
            self.followers = int(float(row[4]))
            self.time_stamp = datetime.strptime(row[8], '%Y-%m-%d %H:%M')
            self.raw_location = row[2]
            self.polarity = float(row[3])
        else:
            self.location = states.location_lookup(row[1])
            self.followers = int(float(row[4]))
            self.time_stamp = _from_csv_date(row[8])
            self.raw_location = row[1]

    def calculate_vader(self, analyzer: SentimentIntensityAnalyzer) -> Tweet:
        """Calculate the vader polarity of this tweet, then return the calling tweet

        Uses the provided sentiment intensity analyzer to calculate polarity"""
        scores = analyzer.polarity_scores(self.tweet)
        self.polarity = scores['compound']
        return self


def from_unfiltered_csv(path: str, analyzer: SentimentIntensityAnalyzer) -> Iterable[Tweet]:
    """Return a generator for tweets from a csv file.

    Yields only tweets determined to match the selection
    criteria for this project.

    Uses provided sentiment intensity analyzer to compute vader polarities"""
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Skip header

        with ThreadPoolExecutor(max_workers=10) as polarity_executor:
            for tweet in futures.as_completed(polarity_executor.submit(
                    Tweet.calculate_vader, Tweet(row), analyzer)
                    for row in reader if _filter_row(row)):
                yield tweet.result()


def from_filtered_csv(path: str) -> Iterable[Tweet]:
    """Return a generator for tweets from a csv file.

    Assumes all tweets in the csv file match the selection
    criteria for this project and that csv contains no header"""
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if _filter_row(row):
                yield Tweet(row, filtered=True)


def filter_and_save(path: str, dest: str, analyzer: SentimentIntensityAnalyzer) -> None:
    """Save a csv of filtered tweets at the specified
    destination using tweets from the specified csv.

    Uses the provided sentiment intensity analyzer to determine vader scores

    Does not write a header"""
    filtered = from_unfiltered_csv(path, analyzer)
    with open(dest, 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        with ThreadPoolExecutor(max_workers=1) as csv_write_queue:
            for tweet in filtered:
                csv_write_queue.submit(writer.writerow, _get_row(tweet))


def _get_row(tweet: Tweet) -> List[str]:
    """Return a list of values to write to a csv file
    representing a tweet"""
    return [tweet.user, tweet.location.code, tweet.raw_location, tweet.polarity, tweet.followers,
            '', '', '', tweet.time_stamp.strftime('%Y-%m-%d %H:%M'),
            tweet.tweet, '', '', '']


def _filter_row(row: List[str]) -> bool:
    """Return whether a row representing a tweet from a csv
    matches the selection criteria for this project

    Specifically matches the following conditions:
        - Follower information is intact
        - Contains a valid date
        - Location contains a US state code or US state name

    Preconditions:
        - len(row) == 13"""
    return row[4] != '' and _from_csv_date(row[8]) is not None \
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


def _print_tweet(tweet: Tweet) -> None:
    """Print a tweet to the console in a human
    readable format
    """
    date = tweet.time_stamp.strftime('%Y-%m-%d %H:%M')
    print(f'User: {tweet.user}\n' +
          f'Location: {tweet.location.name}\n' +
          f'Followers: {tweet.followers}\n' +
          f'Date: {date}\n' +
          f'Tweet: {tweet.tweet}\n')


if __name__ == '__main__':
    import os.path
    UNFILTERED_PATH = '/home/jacob/Downloads/covidvaccine.csv'
    FILTERED_PATH = '/home/jacob/Downloads/filtered_covidvaccine.csv'

    ANALYZER = SentimentIntensityAnalyzer()

    if not os.path.isfile(FILTERED_PATH):
        filter_and_save(UNFILTERED_PATH, FILTERED_PATH, ANALYZER)

    tweets = from_filtered_csv(FILTERED_PATH)

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
