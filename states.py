"""
Functions and global constant state
(as in geographical US state) information
"""

from typing import Optional
from locations import Location

STATES = [Location('AK', 'Alaska', ()),
          Location('AL', 'Alabama', ()),
          Location('AR', 'Arkansas', ()),
          Location('AZ', 'Arizona', ()),
          Location('CA', 'California', ()),
          Location('CO', 'Colorado', ()),
          Location('CT', 'Connecticut', ()),
          Location('DC', 'District of Columbia', ('Washington DC')),
          Location('DE', 'Delaware', ()),
          Location('FL', 'Florida', ()),
          Location('GA', 'Georgia', ()),
          Location('HI', 'Hawaii', ()),
          Location('IA', 'Iowa', ()),
          Location('ID', 'Idaho', ()),
          Location('IL', 'Illinois', ()),
          Location('IN', 'Indiana', ()),
          Location('KS', 'Kansas', ()),
          Location('KY', 'Kentucky', ()),
          Location('LA', 'Louisiana', ()),
          Location('MA', 'Massachusetts', ()),
          Location('MD', 'Maryland', ()),
          Location('ME', 'Maine', ()),
          Location('MI', 'Michigan', ()),
          Location('MN', 'Minnesota', ()),
          Location('MO', 'Missouri', ()),
          Location('MS', 'Mississippi', ()),
          Location('MT', 'Montana', ()),
          Location('NC', 'North Carolina', ()),
          Location('ND', 'North Dakota', ()),
          Location('NE', 'Nebraska', ()),
          Location('NH', 'New Hampshire', ()),
          Location('NJ', 'New Jersey', ()),
          Location('NM', 'New Mexico', ()),
          Location('NV', 'Nevada', ()),
          Location('NY', 'New York', ()),
          Location('OH', 'Ohio', ()),
          Location('OK', 'Oklahoma', ()),
          Location('OR', 'Oregon', ()),
          Location('PA', 'Pennsylvania', ()),
          Location('PR', 'Puerto Rico', ()),
          Location('RI', 'Rhode Island', ()),
          Location('SC', 'South Carolina', ()),
          Location('SD', 'South Dakota', ()),
          Location('TN', 'Tennessee', ()),
          Location('TX', 'Texas', ()),
          Location('UT', 'Utah', ()),
          Location('VA', 'Virginia', ()),
          Location('VT', 'Vermont', ()),
          Location('WA', 'Washington', ()),
          Location('WI', 'Wisconsin', ()),
          Location('WV', 'West Virginia', ()),
          Location('WY', 'Wyoming', ())]


def code_lookup(code: str) -> Location:
    """Return a location with a code matching the provided one.

    Preconditions:
        - len(code) == 2
        - code.upper() == code
        - code.isalpha()"""
    # Binary search for state with matching code
    # Posible because states are in alphabetical order

    lower = 0
    upper = len(STATES)
    pointer = (lower + upper) // 2
    while 0 <= lower < len(STATES) and 0 <= upper <= len(STATES) and STATES[pointer].code != code:
        if code > STATES[pointer].code:
            lower = pointer
        else:  # Must be less because loop doesn't run when is equal
            upper = pointer
        pointer = (lower + upper) // 2
    return STATES[pointer]


def location_lookup(location: str) -> Optional[Location]:
    """Return a location that has either a name,
    state code, or related term matching the
    provided location string.

    Return None if no matching location can be found"""
    # Exhaust state names, then related terms, before
    # finally checking for state codes
    # matches lowercase for state name and
    # related terms but not state code
    # TODO : Look into soundex or similar fuzzy logic for state names
    location_lower = location.lower()
    for state in STATES:
        if state.name.lower() in location_lower:
            return state
    for state in STATES:
        for term in state.related_terms:
            if term.lower() in location_lower:
                return state
    for state in STATES:
        if state.code in location:
            return state
