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
        """

    locations: List[Location]
    analyzer: SentimentIntensityAnalyzer

if __name__ == '__main__':
    pass