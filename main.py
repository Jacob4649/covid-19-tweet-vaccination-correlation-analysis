from datetime import date
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model._glm.glm import _y_pred_deviance_derivative
from app import App
import vaccinations
import tweets
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

    import plotly.express as px
    fig = px.scatter(x=tweet_list, y=vaccine_list,
                     labels=dict(x="Mean VADER Score", y="Vaccination Rate"))

    # calculate regression

    x_array = np.array(tweet_list).reshape(-1, 1)
    y_array = np.array(vaccine_list).reshape(-1, 1)

    regression = LinearRegression().fit(x_array, y_array)

    # plot line of best fit

    base_x = min(tweet_list)
    end_x = max(tweet_list)

    base_y = regression.predict(np.array(base_x).reshape(-1, 1))[0][0]
    end_y = regression.predict(np.array(end_x).reshape(-1, 1))[0][0]

    fig.add_shape(type='line', x0=base_x, y0=base_y, x1=end_x, y1=end_y)

    fig.show()
