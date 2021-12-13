"""
This file defines the dataclass VacRate and helps with orgainzing the data

"""
import csv
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
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
    location: str
    time_stamp: date
    total: float
    daily: float

    def __init__(self, row: List[str]):
        """Initialize an instance of this vaccination rate class
        from a row from a csv

        Preconditions:
            - len(row) == 14"""
        self.location = row[1]
        self.time_stamp = datetime.strptime(row[0], '%Y-%m-%d').date()
        self.total = float(row[2])
        self.daily = float(row[11])


def _filter_row(row: List[str]) -> bool:
    """Return whether a row contains suitable vaccination data"""
    return len(row) == 14 and row[11] != '' and row[2] != ''


def from_csv(filename: str) -> Iterable[VaccinationRate]:
    """Return generator for vaccination rate objects"""

    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the header

        # move disk io to new thread
        with ThreadPoolExecutor(max_workers=1) as read_executor:
            # create filtered rows generator
            filtered_rows = filter(_filter_row, reader)
            # execute io in executor
            for result in read_executor.map(VaccinationRate, filtered_rows):
                yield result


if __name__ == '__main__':
    VACCINATION_PATH = 'C:\\Users\\Jacob\\Downloads\\archive\\vaccination_data.csv'

    rates = from_csv(VACCINATION_PATH)
    for d in rates:
        print(f'{d.location}, {d.time_stamp.isoformat()}, {d.daily}')
