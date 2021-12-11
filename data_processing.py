"""
Module for generating statistic values by date.
"""

import numpy as np
from datetime import date
from typing import List, Tuple, Union
from sklearn.linear_model import LinearRegression


class DailyMetric:
    """Class that wraps around the floating point or integer value of some daily metric"""

    def _is_compatible_date(self, date: date) -> bool:
        """Return whether this metric has a numeric value for a given date"""

    def _get_measurement_value(self, date: date) -> Union[float, int]:
        """Return the value of a numeric metric on a given date"""

    def get(self, date: date) -> Union[float, int]:
        """Return the measurement value for a given date"""
        if (self._is_compatible(date)):
            return self._get_measurement_value(date)
        else:
            raise ValueError("No measurement found for entered date")


class DailyMetricCollection:
    """
    Class containing daily measurements of a specific floating point or integer metric.
    """


class LinearMetric(DailyMetric):
    """Class that uses concrete data values to
    make statistical estimates of the value of a metric at dates where
    concrete data does not exist"""

    _base_date: date
    _regression: LinearRegression
    _integer_outputs: bool

    def __init__(self, data: List[Tuple[date, Union[float, int]]], base_date: date,
                 int_outputs: bool):
        """Create a regression model from a set of datapoints, and specify a base date
        for this linear metric. Also indicate whether outputs should be floating point
        or integer"""
        self._base_date = base_date
        x_data, y_data = self._generate_data(data)
        self._regression = LinearRegression().fit(x_data, y_data)
        self._integer_outputs = int_outputs

    def _convert_date(self, date: date) -> int:
        """Convert a date to an integer offset from a base date"""
        return (date - self._base_date).days

    def _generate_data(self, data: List[Tuple[date, Union[float, int]]]) -> Tuple[np.ndarray, np.ndarray]:
        """Return a tuple containining a tuple of arrays, the first being the
        array of x values to use to train the regression, 
        and the second being an array of y values to use"""
        x_list = [self._convert_date(d[0]) for d in data]
        y_list = [d[1] for d in data]
        return self._convert_numpy(x_list), self._convert_numpy(y_list)

    def _convert_numpy(self, data: List[Union[float, int]]) -> np.ndarray:
        """Return the specified list converted to a numpy array"""
        return np.array(data).reshape(-1, 1)

    def _get_measurement_value(self, date: date) -> Union[float, int]:
        """Return the estimated value of a metric at the specified date"""
        date_array = [self._convert_date(date)]
        input_data = self._convert_numpy(date_array)
        output = self._regression.predict(input_data)
        return output[0][0]


class LinearExtrapolationMetric:
    """Class that extrapolates the value of a metric at
    a specific date by using the values of the metric leading
    up to that date"""


class LinearInterpolationMetric:
    """Class that interpolates the value of a metric at a specific date
    by using the values of the metric leading up to that date"""


class SingleDateMetric(DailyMetric):
    """Metric for a single date

    Attributes:
        - date: the date for this metric
        - value: the value for this metric"""

    value: Union[float, int]
    date: date

    def __init__(self, date: date, value: Union[float, int]):
        """Sets the value and date for this single date metric"""

    def _get_measurement_value(self, date: date) -> Union[float, int]:
        """Gets the value stored by this single date metric"""
        return self.value

    def _is_compatible_date(self, date: date) -> bool:
        """Return whether the provided date is the one this
        single date metric is for"""
        return date == self.date
