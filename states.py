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
from typing import Optional
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


def code_lookup(code: str, states_list: list[Location]) -> Location:
    """Return a location with a code matching the provided one.
    Preconditions:
        - len(code) == 2
        - code.upper() == code
        - code.isalpha()"""
    # Binary search for state with matching code
    # Posible because states are in alphabetical order

    lower = 0
    upper = len(states_list)
    pointer = (lower + upper) // 2
    while 0 <= lower < len(states_list) and \
            0 <= upper <= len(states_list) and \
            states_list[pointer].code != code:
        if code > states_list[pointer].code:
            lower = pointer
        else:  # Must be less because loop doesn't run when is equal
            upper = pointer
        pointer = (lower + upper) // 2
    return states_list[pointer]


def location_lookup(location: str, states_list: list[Location]) -> Optional[Location]:
    """Return a location that has either a name,
    state code, or related term matching the
    provided location string.
    Return None if no matching location can be found"""
    # Exhaust state names, then related terms, before
    # finally checking for state codes
    # matches lowercase for state name and
    # related terms but not state code
    location_lower = location.lower()
    for state in states_list:
        if state.name.lower() in location_lower:
            return state
    for state in states_list:
        for term in state.related_terms:
            if term.lower() in location_lower:
                return state
    for state in states_list:
        if state.code in location:
            return state
    return None


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
