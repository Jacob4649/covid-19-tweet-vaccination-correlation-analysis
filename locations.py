"""Handles recognized locations"""


from dataclasses import dataclass
from typing import Tuple


@dataclass
class Location(object):
    """Class representing a single location (i.e. a state)

    Attributes:
        - code: The location code, a 2 digit
        key corresponding to this location
        - name: The name for this location
        - related_terms: A tuple of terms related to this location

    Representation Invariants:
        - len(code) == 2
        - code.upper() == code
        - code.isalpha()"""

    code: str
    name: str
    related_terms: Tuple
