"""
Location Grouping

Module Description
==================
Module with functions for manipulating tweets and vaccine rates by their location

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Jacob Klimczak, Ryan Merheby and Sean Ryan.
"""


from typing import Dict, List, Tuple
import datetime
from tweets import Tweet
from vaccinations import VaccinationRate
from data_processing import DailyMetricCollection, \
    average_metrics, calculate_correlation, generate_metrics


def location_stats(vaccine_dict: Dict[str, List[VaccinationRate]],
                   tweet_dict: Dict[str, List[Tweet]], code: str, start_date: datetime.date,
                   end_date: datetime.date) -> Tuple[List[float], List[float]]:
    """Return a tuple with daily mean vader scores, and daily mean vaccinations
    for the specified state between the start and end dates

    Preconditions:
        - len(code) == 2
        - code is a valid state code"""
    tweets_metrics = generate_metrics(
        tweet_dict[code], lambda tweet: (tweet.time_stamp.date(), tweet.polarity))
    vaccines_metrics = generate_metrics(
        vaccine_dict[code], lambda vaccine: (vaccine.time_stamp, vaccine.daily))

    average_polarity_of_tweets = average_metrics(tweets_metrics)
    average_rate_of_vaccines = average_metrics(vaccines_metrics)

    tweet_data_collection = DailyMetricCollection(
        average_polarity_of_tweets, False)
    vaccine_data_collection = DailyMetricCollection(
        average_rate_of_vaccines, True)

    range_of_tweets = tweet_data_collection.get(start_date, end_date)
    range_of_vaccines = vaccine_data_collection.get(start_date, end_date)

    tweet_array = list(range_of_tweets)
    vaccine_array = list(range_of_vaccines)

    return tweet_array, vaccine_array


def location_correlation(vaccine_dict: Dict[str, List[VaccinationRate]],
                         tweet_dict: Dict[str, List[Tweet]],
                         start_date: datetime.date, end_date: datetime.date) -> Dict[str, float]:
    """Return a dictionary mapping state codes to the correlation
    between state vaccination and state twitter discourse"""
    output = {}
    for key in tweet_dict:
        if key in vaccine_dict:
            a, b = location_stats(
                vaccine_dict, tweet_dict, key, start_date, end_date)
            c = calculate_correlation(a, b)
            output[key] = c
    return output


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': ['tweets', 'vaccinations', 'datetime', 'data_processing'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import doctest
    doctest.testmod()
