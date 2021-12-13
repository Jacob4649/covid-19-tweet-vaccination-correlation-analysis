"""
This file defines the dataclass VacRate and helps with orgainzing the data

"""
from datetime import date
from typing import List


class VaccinationRate:
    """Stores the date of vaccination data, the location of vaccination data,
    the total amount of vaccinated people in that location, and daily vaccination

    Attributes:
        - location: the name of the location
        - time_stamp: the date the data was taken
        - total_vaccination: the total amount of people vaccinated at that time and location
        - daily_vaccination: the amount of people vaccinated daily at that location and time

    """
    location: str
    time_stamp: time_stamp
    total_vaccination: float
    daily_vaccination: float

    def __init__(self, row: List[str]):
        """Initialize an instance of this vaccination rate class
        from a row from a csv

        Preconditions:
            - len(row) == 13"""
        self.location = row[1]
        self.time_stamp = date.strptime(row[0], '%Y-%m-%d')
        self.total_vaccination = float(row[2])
        self.daily_vaccination = float(row[11])
