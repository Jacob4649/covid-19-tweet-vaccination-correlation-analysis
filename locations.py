"""
Locations

Module Description
==================
Defines Location data type

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Jacob Klimczak, Ryan Merheby and Sean Ryan.
"""


from dataclasses import dataclass
from typing import Tuple


@dataclass
class Location():
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


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': [],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })
