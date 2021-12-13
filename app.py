"""Contains manager class with app state"""

from nltk.sentiment import SentimentIntensityAnalyzer
from locations import Location
from typing import List


class App:
    """Class representing the state of the application at a given point
    in time

    Attributes:
        - locations: a list of locations
        - analyzer: the sentiment analyzer to use
        - tweet_path: path to tweet dataset
        - vaccine path: path to vaccine dataset
        """

    locations: List[Location]
    analyzer: SentimentIntensityAnalyzer
    tweet_path: str
    vaccine_path: str

    def __init__(self):
        """Initialize app object"""


if __name__ == '__main__':
    pass
