"""
States

Module Description
==================
Contains functions that unpack state information into location objects and
search for attributes in those objects.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Jacob Klimczak, Ryan Merheby and Sean Ryan.
"""

import json
from locations import Location


def unpack_json_into_locations(filename: str) -> list[Location]:
    """Serialize the attributes of location objects into a JSON file.
    Preconditions:
    - filename is a valid file
    - filename[-4:] == 'json'
    - with open(filename, 'r') as f:
        json_data = json.load(f)
        type(json_data) == list
        all(type(json_object) == dict for json_object in json_data)"""

    states_so_far = []
    try:
        with open(filename, 'r') as f:
            json_data = json.load(f)
        for state_data in json_data:
            code = state_data["code"]
            name = state_data["name"]
            related_terms = state_data["related_terms"]
            state = Location(code, name, related_terms)
            states_so_far.append(state)
    except IOError:
        print("The requested file cannot be loaded from.")

    return states_so_far


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': ['json',
                          'os',
                          'locations'],
        'allowed-io': ['unpack_json_into_locations'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })
    import doctest

    doctest.testmod()
