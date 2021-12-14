from datetime import date
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model._glm.glm import _y_pred_deviance_derivative
from app import App
import vaccinations
import tweets
import visualization
from data_processing import DailyMetricCollection, average_metrics, generate_metrics, location_dict


if __name__ == '__main__':
    app = App()
    raw_tweets = tweets.from_csv(app.tweet_path, app)
    raw_vaccinations = vaccinations.from_csv(app.vaccine_path, app)

    # location_tweets = location_dict(raw_tweets,
    #                                 lambda tweet: tweet.location)
    # location_vaccines = location_dict(raw_vaccinations,
    #                                   lambda rate: rate.location)

    tweet_metric = generate_metrics(
        raw_tweets, lambda tweet: (tweet.time_stamp.date(), tweet.polarity))
    vaccine_metric = generate_metrics(
        raw_vaccinations, lambda vaccine: (vaccine.time_stamp, vaccine.daily))

    average_tweet_polarity = average_metrics(tweet_metric)
    average_vaccine_rate = average_metrics(vaccine_metric)

    tweet_collection = DailyMetricCollection(average_tweet_polarity, False)
    vaccine_collection = DailyMetricCollection(average_vaccine_rate, True)

    start = date(2021, 2, 28)
    end = date(2021, 11, 1)

    tweet_range = tweet_collection.get(start, end)
    vaccine_range = vaccine_collection.get(start, end)

    tweet_list = list(tweet_range)
    vaccine_list = list(vaccine_range)

    diff = (end - start).days + 1

    fig = visualization.vaccination_twitter_plot(
        tweet_list, vaccine_list, 'Vaccination Rate As Related To Ongoing Twitter Discourse')

    fig.show()
