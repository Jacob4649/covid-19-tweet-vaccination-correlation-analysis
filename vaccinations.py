"""
Vaccinations

Module Description
==================
Bundles data about vaccination rates into a dataclass and contains functions that 
help organize that data

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Jacob Klimczak, Ryan Merheby and Sean Ryan.
"""

import csv
from app import App
import states
from locations import Location
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import datetime
from typing import Iterable, List


class VaccinationRate:
    """Stores the date of vaccination data, the location of vaccination data,
    the total amount of vaccinated people in that location, and daily vaccination

    Attributes:
        - location: the name of the location
        - time_stamp: the date the data was taken
        - total: the total amount of people vaccinated at that time and location
        - daily: the amount of people vaccinated daily at that location and time

    """
    location: Location
    time_stamp: datetime.date
    total: float
    daily: float

    def __init__(self, row: List[str], app: App):
        """Initialize an instance of this vaccination rate class
        from a row from a csv, and an app state bundle

        Preconditions:
            - len(row) == 14"""
        self.location = app.location_lookup(row[1])
        self.time_stamp = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
        self.total = float(row[2])
        self.daily = float(row[11])


def _filter_row(row: List[str], app: App) -> bool:
    """Return whether a row contains suitable vaccination data,
    takes a row and an app state bundle"""
    return len(row) == 14 and row[11] != '' and row[2] != '' \
        and app.location_lookup(row[1]) is not None


def from_csv(filename: str, app: App) -> Iterable[VaccinationRate]:
    """Return generator for vaccination rate objects, from
    the provided csv, using the provided app state"""

    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the header

        def vaccine_filter(row: List[str]) -> bool:
            """Return whether a vaccination rate should be created from a csv row

            Function for use with map that filters csv rows"""
            return _filter_row(row, app)

        # create filtered rows generator
        filtered_rows = filter(vaccine_filter, reader)

        def create_rate(row: List[str]) -> VaccinationRate:
            """Return a vaccination rate created from a csv row

            Function for use with map that creates a
            vaccination rate from a csv row"""
            return VaccinationRate(row, app)

        # move disk io to new thread
        with ThreadPoolExecutor(max_workers=1) as read_executor:
            # execute io in executor
            for result in read_executor.map(create_rate, filtered_rows):
                yield result


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
