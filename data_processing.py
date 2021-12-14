"""
Module for generating statistic values by date.
"""

import numpy as np
from scipy.stats import pearsonr
from datetime import date, timedelta
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union
from locations import Location
from sklearn.linear_model import LinearRegression
from tweets import Tweet
from vaccinations import VaccinationRate


class DailyMetric:
    """Class that wraps around the floating point or integer value of some daily metric"""

    def is_compatible_date(self, date: date) -> bool:
        """Return whether this metric has a numeric value for a given date"""

    def _get_measurement_value(self, date: date) -> Union[float, int]:
        """Return the value of a numeric metric on a given date"""

    def get(self, date: date) -> Union[float, int]:
        """Return the measurement value for a given date"""
        if (self.is_compatible_date(date)):
            return self._get_measurement_value(date)
        else:
            raise ValueError("No measurement found for entered date")


class SingleDateMetric(DailyMetric):
    """Metric for a single date

    Attributes:
        - date: the date for this metric
        - value: the value for this metric"""

    value: Union[float, int]
    date: 'date'

    def __init__(self, date: date, value: Union[float, int]):
        """Sets the value and date for this single date metric"""
        self.date = date
        self.value = value

    def _get_measurement_value(self, date: date) -> Union[float, int]:
        """Gets the value stored by this single date metric"""
        return self.value

    def is_compatible_date(self, date: date) -> bool:
        """Return whether the provided date is the one this
        single date metric is for"""
        return date == self.date


class LinearMetric(DailyMetric):
    """Class that uses concrete data values to
    make statistical estimates of the value of a metric at dates where
    concrete data does not exist"""

    _base_date: date
    _regression: LinearRegression
    _integer_outputs: bool

    def __init__(self, data: List[Tuple[date, Union[float, int]]],
                 int_outputs: bool):
        """Create a regression model from a set of datapoints.
        Also indicate whether outputs should be floating point
        or integer"""
        self._base_date = data[0][0]
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
        out_value = output[0][0]
        if self._integer_outputs:
            return round(out_value)
        else:
            return out_value


class LinearExtrapolationMetric(LinearMetric):
    """Class that extrapolates the value of a metric at
    a specific date by using the values of the metric leading
    up to that date"""

    _main_date: date
    _end: bool

    def __init__(self, data: List[SingleDateMetric], end: bool, int_outputs: bool):
        """Initialize a linear interpolation metric from the provided
        sorted list of single date metrics, and also indicate whether
        outputs should be integer or floating point, and which endpoint to extrapolate from

        Preconditions:
            - data = sorted(data, key=lamba a: a.date)
            - len(data) > 1"""
        super().__init__([(metric.date, metric.value)
                          for metric in data], int_outputs)
        self._end = end
        if end:
            self._main_date = data[-1].date
        else:
            self._main_date = data[0].date

    def is_compatible_date(self, date: date) -> bool:
        if self._end:
            return date > self._main_date
        else:
            return date < self._main_date


class LinearInterpolationMetric(LinearMetric):
    """Class that interpolates the value of a metric at a specific date
    by using the values of the metric leading up to that date"""

    _start_date: date
    _end_date: date

    def __init__(self, data: List[SingleDateMetric], start: date, end: date, int_outputs: bool):
        """Initialize a linear interpolation metric from the provided
        sorted list of single date metrics, and also indicate whether
        outputs should be integer or floating point

        Preconditions:
            - data = sorted(data, key=lamba a: a.date)
            - len(data) > 1"""
        super().__init__([(metric.date, metric.value)
                          for metric in data], int_outputs)
        self._start_date = start
        self._end_date = end

    def is_compatible_date(self, date: date) -> bool:
        return self._start_date <= date <= self._end_date


class DailyMetricCollection:
    """
    Class containing daily measurements of a specific floating point or integer metric.

    Attributes:
        - interpolation_range: How far around an interpolation index to
        use when interpolating
        - extrapolation_range: How far before or after an extrapolation
        index to use when extrapolating

    Representation Invariants:
        - self.extrapolation_range > 1
        - self.interpolation_range > 1
        - len(self._metrics) > self.interpolation_range
        - len(self._metrics) > self.extrapolation_range
    """

    _integer_outputs: bool
    extrapolation_range: int
    interpolation_range: int
    _metrics: List[SingleDateMetric]

    def __init__(self, data: List[SingleDateMetric], int_outputs: bool):
        """Initialize a daily metric collection using a list of single
        date metrics, extrapolating past the endpoints, and interpolating
        between any gaps.

        Indicate the output type of this collection, integer, or float"""
        self.interpolation_range = 3
        self.extrapolation_range = 3
        self._integer_outputs = int_outputs
        self._metrics = sorted(data, key=lambda a: a.date)

    def _get_data_around(self, index: int, data_range: int) -> List[SingleDateMetric]:
        """Gets single date metrics around a specified metric index

        Preconditions:
            - 0 <= index < len(self._metrics)"""
        forward_outputs = []
        rear_outputs = []
        forward = index + 1
        rear = index
        while len(forward_outputs) < data_range and forward < len(self._metrics):
            potential = self._metrics[forward]
            forward_outputs.append(potential)
            forward += 1
        while len(rear_outputs) < data_range and rear >= 0:
            potential = self._metrics[rear]
            rear_outputs.insert(0, potential)
            rear -= 1
        return rear_outputs + forward_outputs

    def _find_index(self, date: date) -> Tuple[int, bool]:
        """Return a tuple containing a bool indicating whether the desired date is
        within the dates of the endpoints of _metrics, and if it is, the 
        index of the single date metric for the specified date,
        or else the index of the single date metric with the largest date
        less than the desired one. If the date is not within _metrics, the index returned
        is 0 if it is below all dates in _metrics, or 1 if it is above all dates in metrics"""
        lower = 0
        upper = len(self._metrics)
        pointer = (lower + upper) // 2
        # binary search for suitable index
        while 0 <= lower < len(self._metrics) and 0 <= upper <= len(self._metrics) \
                and upper != lower:
            metric = self._metrics[pointer]
            if date > metric.date:  # too small: upper endpoint, lower bound, correct index
                if pointer == len(self._metrics) - 1:
                    return 1, True  # if checking biggest date, and desired is still bigger
                # desired date less than date at next index
                elif date < self._metrics[pointer + 1].date:
                    return pointer, False
                else:
                    lower = pointer
            elif date < metric.date:  # too big: upper bound, lower endpoint
                if pointer == 0:  # if checking smallest date and desired is still smaller
                    return 0, True
                else:
                    upper = pointer
            else:  # correct date
                return pointer, False
            pointer = (lower + upper) // 2
        if upper == lower:
            return upper, False
        else:
            raise RuntimeError("_find_index failed to locate a suitable index")

    def _interpolate(self, index: int) -> LinearInterpolationMetric:
        """Returns linear interpolation metric around the specified index in _metrics

        Preconditions:
            - 0 <= index < len(self.m_metrics) - 1"""

        data = self._get_data_around(index, self.interpolation_range)

        start = self._metrics[index].date
        end = self._metrics[index + 1].date

        return LinearInterpolationMetric(data, start, end, self._integer_outputs)

    def _extrapolate(self, end: bool) -> LinearExtrapolationMetric:
        """Returns linear extrapolation metric around the beginning or end of _metrics.

        End parameter specifies whether the beginning or end should be
        used"""

        index = 0
        if end:
            index = len(self._metrics) - 1

        data = self._get_data_around(index, self.extrapolation_range)

        return LinearExtrapolationMetric(data, end, self._integer_outputs)

    def get(self, start: date, end: date) -> Iterable[SingleDateMetric]:
        """Return a generator for single date metrics between
        the start and end dates based on the data inputted into this
        daily metric collection

        Preconditions:
            - start <= end"""

        diff = (end - start).days
        start_metric, endpoint = self._find_index(start)

        i = 0
        current_date = start + timedelta(days=i)

        next_index = start_metric + 1

        if endpoint:  # start with extrapolation
            if start_metric == 0:  # extrapolate from before
                current_metric = self._extrapolate(False)
                next_index = 0
            else:  # extrapolate from after
                current_metric = self._extrapolate(True)
                next_index = len(self._metrics) + 1
        # start on metric
        elif current_date == self._metrics[start_metric].date:
            current_metric = self._metrics[start_metric]
        else:  # start with interpolation
            current_metric = self._interpolate(start_metric)

        # start yielding values
        while i <= diff:
            yield current_metric.get(current_date)
            i += 1
            current_date = current_date + timedelta(days=1)
            if next_index == len(self._metrics):
                # extrapolate endpoint
                current_metric = self._extrapolate(True)
            elif next_index < len(self._metrics) and self._metrics[next_index].is_compatible_date(current_date):
                # move to next metric
                current_metric = self._metrics[next_index]
                next_index += 1
            elif not current_metric.is_compatible_date(current_date):
                # interpolate
                current_metric = self._interpolate(next_index - 1)
                next_index += 1


def generate_metrics(data: Iterable, transform:
                     Callable[[Any], Tuple[date, Union[float, int]]]) \
        -> Iterable[SingleDateMetric]:
    """Return a generator for single date metrics using the specified data,
    and a callable that transforms each entry in the provided data, into a tuple containing
    a date and a value"""
    for point in data:
        date, value = transform(point)
        yield SingleDateMetric(date, value)


def average_metrics(data: Iterable[SingleDateMetric]) -> List[SingleDateMetric]:
    """Return a list of single date metrics containing the average value
    for each provided single date metric on their given date"""
    dates = {}
    for point in data:
        if point.date in dates:
            dates[point.date].append(point)
        else:
            dates[point.date] = [point]

    return [SingleDateMetric(date, sum(d.value for d in dates[date])/len(dates[date]))
            for date in dates]


def location_dict(data: Iterable, location_get: Callable[[Any], Location]) -> Dict[str, List[Any]]:
    """Return a dictionary of location codes mapped to lists of objects at those locations.

    Uses the objects in the provided data iterable, and the location_get function
    to get the location of items in data"""
    locations = {}
    for item in data:
        location = location_get(item)
        if location.code in locations:
            locations[location.code].append(item)
        else:
            locations[location.code] = [item]
    return locations


def location_stats(vaccine_dict: Dict[str, List[VaccinationRate]],
                   tweet_dict: Dict[str, List[Tweet]], code: str, start: date,
                   end: date) -> Tuple[List[float], List[float]]:
    """Return a tuple with daily mean vader scores, and daily mean vaccinations
    for the specified state between the start and end dates

    Preconditions:
        - len(code) == 2
        - code is a valid state code"""
    tweets = tweet_dict[code]
    vaccines = vaccine_dict[code]

    tweet_metric = generate_metrics(
        tweets, lambda tweet: (tweet.time_stamp.date(), tweet.polarity))
    vaccine_metric = generate_metrics(
        vaccines, lambda vaccine: (vaccine.time_stamp, vaccine.daily))

    average_tweet_polarity = average_metrics(tweet_metric)
    average_vaccine_rate = average_metrics(vaccine_metric)

    tweet_collection = DailyMetricCollection(average_tweet_polarity, False)
    vaccine_collection = DailyMetricCollection(average_vaccine_rate, True)

    tweet_range = tweet_collection.get(start, end)
    vaccine_range = vaccine_collection.get(start, end)

    tweet_list = list(tweet_range)
    vaccine_list = list(vaccine_range)

    return tweet_list, vaccine_list


def calculate_correlation(tweets: List[float], vaccines: List[float]) -> float:
    """Return the pearson's correlation coefficient between
    the lists of tweet and vaccine information"""
    return pearsonr(tweets, vaccines)[0]
