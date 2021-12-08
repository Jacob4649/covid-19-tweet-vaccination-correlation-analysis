"""
This file defines the dataclass VacRate and helps with orgainzing the data

"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VacRate:
    """A custom data type that stores the date of vaccination data, the location of vaccination data,
    the total amount of vaccinated people in that location, and daily vaccination

    Attributes:
        - location: the name of the location
        - date: the date the data was taken
        - total_vac: the total amount of people vaccinated at that time and location
        - daily_vac: the amount of people vaccinated daily at that location and time

    """
    location: str
    date: datetime
    total_vac: float
    daily_vac: float
