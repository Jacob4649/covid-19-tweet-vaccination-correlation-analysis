from datetime import date
from typing import Dict, List, Tuple
from app import App
import vaccinations
import tweets
import visualization
from data_processing import DailyMetricCollection, average_metrics, generate_metrics, location_dict, calculate_correlation
from tweets import Tweet
from vaccinations import VaccinationRate
import nltk
import ssl


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


def location_correlation(vaccine_dict: Dict[str, List[VaccinationRate]],
                         tweet_dict: Dict[str, List[Tweet]],
                         start: date, end: date) -> Dict[str, float]:
    """Return a dictionary mapping state codes to the correlation
    between state vaccination and state twitter discourse"""
    output = {}
    for key in tweet_dict:
        if key in vaccine_dict:
            a, b = location_stats(
                vaccine_dict, tweet_dict, key, start, end)
            c = calculate_correlation(a, b)
            output[key] = c
    return output


if __name__ == '__main__':
    # downlad vader lexicon
    try:
        # disable ssl (necessary to download vader lexicon)
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('vader_lexicon')

    # launch app
    app = App()

    # import from datasets
    raw_tweets = list(tweets.from_csv(app.tweet_path, app))
    raw_vaccinations = list(vaccinations.from_csv(app.vaccine_path, app))

    # choose start and end dates
    start = date(2021, 2, 28)
    end = date(2021, 11, 1)

    # split data by state
    location_tweets = location_dict(raw_tweets,
                                    lambda tweet: tweet.location)
    location_vaccines = location_dict(raw_vaccinations,
                                      lambda rate: rate.location)

    # calculate correlation for each state
    correlations = location_correlation(
        location_vaccines, location_tweets, start, end)

    # fill in incomplete data by interpolating between existing datapoints
    tweet_metric = generate_metrics(
        raw_tweets, lambda tweet: (tweet.time_stamp.date(), tweet.polarity))
    vaccine_metric = generate_metrics(
        raw_vaccinations, lambda vaccine: (vaccine.time_stamp, vaccine.daily))

    average_tweet_polarity = average_metrics(tweet_metric)
    average_vaccine_rate = average_metrics(vaccine_metric)

    tweet_collection = DailyMetricCollection(average_tweet_polarity, False)
    vaccine_collection = DailyMetricCollection(average_vaccine_rate, True)

    # get interpolated data between start and end dates
    tweet_range = tweet_collection.get(start, end)
    vaccine_range = vaccine_collection.get(start, end)

    tweet_list = list(tweet_range)
    vaccine_list = list(vaccine_range)

    # visualize data
    fig = visualization.vaccination_twitter_plot(
        tweet_list, vaccine_list, 'Vaccination Rate As Related To Ongoing Twitter Discourse')

    chloropleth = visualization.chloropleth(
        correlations, 'Correlation Between Twitter Discourse And Vaccination Rate',
        'Correlation', app)

    # setup output file
    figures = []
    figures.append(visualization.unwrap_figure(fig.to_html()))

    figures.append(visualization.text_block(
        'The graph above shows the average vaccination rate in the US on a given day ' +
        'as a function of the average sentiment of Twitter discourse on the same day. ' +
        'From this graph we can see that days with higher intensity sentiments (' +
        'reflecting more positive views towards the vaccine) tend to correspond to ' +
        'higher vaccination rates. The reverse is also true. The linear model we produced ' +
        'is shown as a line on the graph. The absolute values of its residuals are shown ' +
        'towards the bottom.'))

    figures.append(visualization.unwrap_figure(chloropleth.to_html()))

    figures.append(visualization.text_block(
        'The above graph shows the correlations between vaccination rate and vaccine perception in Twitter discourse. ' +
        'Darker states have stronger correlations, blue corresponds to negative correlations, and red corresponds to ' +
        'positive correlations. A strong positive correlation means that the population\'s feelings about the vaccine ' +
        'on Twitter reflect their rate of getting the vaccine. A strong negative correlation means the opposite. The ' +
        'weakly correlated states are in between. Their feelings on Twitter do not seem to correspond to their rate ' +
        'of getting the vaccine in any way.'))

    # noteable states
    figures.append(visualization.text_block(
        '<div style="text-align: center; font-size: 24pt; padding: 24pt">NOTABLE STATES</div>'))

    figures.append(visualization.text_block('Here are a few close up graphs of the notable states in ' +
                                            'this analysis. The 3 most and 3 least correlated states ' +
                                            'are shown. Also worth noting, is that no data is available ' +
                                            'on West Virgina, as no Tweets were able to be filtered out for it.'))

    # sort states by correlation
    sort = sorted(correlations.keys(),
                  key=lambda state: correlations[state], reverse=True)

    # first most correlated
    most = sort[0]
    most_tweets, most_vaccine = location_stats(location_vaccines, location_tweets,
                                               most, start, end)

    most_fig = visualization.vaccination_twitter_plot(
        most_tweets, most_vaccine, f'Vaccination Information For {app.location_code_lookup(most).name}')

    figures.append(visualization.unwrap_figure(most_fig.to_html()))

    visualization.output(figures, app.output_path, app.template_path)
