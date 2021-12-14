"""Contains manager class with app state"""

from nltk.sentiment import SentimentIntensityAnalyzer
from locations import Location
from typing import List, Optional
import states
from data_processing import generate_metrics, average_metrics, location_dict
import os


class App:
    """Class representing the state of the application at a given point
    in time

    Attributes:
        - locations: a list of locations
        - analyzer: the sentiment analyzer to use
        - tweet_path: path to tweet dataset
        - vaccine path: path to vaccine dataset
        - template_path: path to find output template
        - output_path: path to write output to
        """

    locations: List[Location]
    analyzer: SentimentIntensityAnalyzer
    tweet_path: str
    vaccine_path: str
    template_path: str
    output_path: str

    def __init__(self):
        """Initialize app object"""
        self.tweet_path = _get_dataset('twitter.csv')
        self.vaccine_path = _get_dataset('vaccine.csv')
        self.template_path = _get_resource('output-template.html')
        self.output_path = _get_absolute_path('output.html')
        self.locations = states.STATES
        self.analyzer = SentimentIntensityAnalyzer()

    def location_code_lookup(self, code: str) -> Location:
        """Return a location with a code matching the provided one.

        Preconditions:
            - len(code) == 2
            - code.upper() == code
            - code.isalpha()"""
        # Binary search for state with matching code
        # Posible because states are in alphabetical order

        lower = 0
        upper = len(self.locations)
        pointer = (lower + upper) // 2
        while 0 <= lower < len(self.locations) and 0 <= upper <= len(self.locations) \
                and self.locations[pointer].code != code:
            if code > self.locations[pointer].code:
                lower = pointer
            else:  # Must be less because loop doesn't run when is equal
                upper = pointer
            pointer = (lower + upper) // 2
        return self.locations[pointer]

    def location_lookup(self, location: str) -> Optional[Location]:
        """Return a location that has either a name,
        state code, or related term matching the
        provided location string.

        Return None if no matching location can be found"""
        # Exhaust state names, then related terms, before
        # finally checking for state codes
        # matches lowercase for state name and
        # related terms but not state code
        location_lower = location.lower()
        for state in self.locations:
            if state.name.lower() in location_lower:
                return state
        for state in self.locations:
            for term in state.related_terms:
                if term.lower() in location_lower:
                    return state
        for state in self.locations:
            if _contains_word(location, state.code):
                return state


def _contains_word(string: str, word: str) -> bool:
    """Return whether an input string contains a case matched version
    of the specified word"""
    return string == word or ' ' + word + ' ' in string or \
        (len(string) > len(word) and (string[0:len(word) + 1] == word + ' '
                                      or string[-len(word) - 1:] == ' ' + word))


def _get_absolute_path(path: str) -> str:
    """Return the absolute path of the specified relative path"""
    return os.path.dirname(
        os.path.realpath(__file__)) + os.path.sep + path


def _get_resource(path: str) -> str:
    """Return the path to an item in the resources directory using the
    name of the file"""
    return _get_absolute_path(f'Resources{os.path.sep}{path}')


def _get_dataset(path: str) -> str:
    """Return the path to an item in the datasets directory using the
    name of the file"""
    return _get_absolute_path(f'Datasets{os.path.sep}{path}')


if __name__ == '__main__':
    pass
