"""csc110-project
This file helps filter the data from the vac_data.csv file into a list[list[VacRate]]
that the rest of the system can work with.
"""
import csv
from datetime import datetime
from vaccinations import VaccinationRate


def load_data(filename: str) -> list[list[VaccinationRate]]:
    """Return a list of vac_rates for each state of the US based on the data in filename. Each list is the data from one
    location, with the dates in the order from oldest to newest.

    The data in filename is in a csv format with 14 columns. What the columns represent are in the header of the CVC file.
    """

    with open(filename) as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # skip the header

        # an accumulator that helps create the lists
        vac_rate_so_far = []
        location = ''
        current_list = []
        for row in reader:
            # TODO: also add another part to this if statement that only allows for the US states described in the JSON file to be filtered
            if row[2] != '' and row[11] != '':
                if location != row[1] and current_list != []:
                    vac_rate_so_far.append(current_list)
                    current_list = []
                location = row[1]
                current_list = current_list + [VaccinationRate(row)]
    return vac_rate_so_far
