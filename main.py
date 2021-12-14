"""
Main

Module Description
==================
Entry point for the application

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Jacob Klimczak, Ryan Merheby and Sean Ryan.
"""
import datetime
import ssl
import nltk
import plotly.express as px
from app import App
import vaccinations
import tweets
import visualization
from data_processing import DailyMetricCollection, average_metrics, generate_metrics, location_dict
from location_grouping import location_stats, location_correlation


if __name__ == '__main__':
    # downloading vader lexicon
    try:
        # disabling ssl checking
        # downloading vader lexicon may not work on some machines without disabling this
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
    start = datetime.date(2021, 2, 28)
    end = datetime.date(2021, 11, 1)
    half = start + datetime.timedelta(days=((end - start).days / 2))

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
        tweet_list, vaccine_list,
        'Vaccination Rate As Related To Ongoing Twitter Discourse In The US')

    chloropleth = visualization.chloropleth(
        correlations, 'Correlation Between Twitter Discourse And Vaccination Rate',
        'Correlation', app)

    # setup output file
    figures = []
    figures.append(visualization.unwrap_figure(fig.to_html()))

    figures.append(visualization.text_block(
        'The graph above shows the average vaccination rate per state in the US on a given day'
        + ' as a function of the average sentiment of Twitter discourse on the same day.'
        + ' From this graph we can see that days with higher intensity sentiments ('
        + ' reflecting more positive views towards the vaccine) tend to correspond to'
        + ' higher vaccination rates. The reverse is also true. The linear model we produced'
        + ' is shown as a line on the graph. The absolute values of its residuals are shown'
        + ' towards the bottom.'))

    figures.append(visualization.unwrap_figure(chloropleth.to_html()))

    figures.append(visualization.text_block(
        'The above graph shows the correlations between vaccination rate and vaccine perception'
        + ' in Twitter discourse. Darker states have stronger correlations, blue corresponds to'
        + ' negative correlations, and red corresponds to positive correlations. A strong positive'
        + ' correlation means that the population\'s feelings about the vaccine on Twitter'
        + ' reflect their rate of getting the vaccine. A strong negative correlation'
        + ' means the opposite. The weakly correlated states are in between. Their'
        + ' feelings on Twitter do not seem to correspond to their rate of getting the'
        + ' vaccine in any way.'))

    # noteable states
    figures.append(visualization.text_block(
        '<div style="text-align: center; font-size: 24pt; padding: 24pt">NOTABLE STATES</div>'))

    figures.append(visualization.text_block('Here are a few close up graphs of the notable'
                                            + ' states in this analysis. The 3 most and 3 least '
                                            + ' correlated states are shown. Also worth noting, '
                                            + ' is that no data is available'
                                            + ' on states where no Tweets were able to be filtered'
                                            + ' out for.'))

    # sort states by correlation
    sort = sorted(correlations.keys(),
                  key=lambda state: correlations[state], reverse=True)

    def show_correlated_state(index: str, title: str) -> None:
        """Add the state with the specified index in sort
        to be shown in the output with the specified title information"""
        most = sort[index]
        most_tweets, most_vaccine = location_stats(location_vaccines, location_tweets,
                                                   most, start, end)

        most_fig = visualization.vaccination_twitter_plot(
            most_tweets, most_vaccine, f'Vaccination Information For The {title} '
            + f'({app.location_code_lookup(most).name})')

        figures.append(visualization.unwrap_figure(most_fig.to_html()))

    # show correlated states
    show_correlated_state(0, 'Most Positively Correlated State')
    show_correlated_state(1, 'Second Most Positively Correlated State')
    show_correlated_state(2, 'Third Most Positively Correlated State')
    show_correlated_state(-3, 'Third Most Negatively Correlated State')
    show_correlated_state(-2, 'Second Most Negatively Correlated State')
    show_correlated_state(-1, 'Most Negatively Correlated State')

    # modeled second half
    figures.append(visualization.text_block(
        '<div style="text-align: center; font-size: 24pt; padding: 24pt">MODEL PREDICTIONS</div>'))

    figures.append(visualization.text_block(
        'Here we will examine how well a linear model could have predicted vaccination'
        + ' rates based on Twitter data at an arbitrary moment in time. The graph below has'
        + ' the same data as the first graph in this report, but this time, the line of best'
        + ' fit was calculated using only datapoints from the first half of our date range.'
        + ' The data used to create this model is also displayed on the graph below.'))

    # filter for data only from first half
    half_tweet_range = tweet_collection.get(start, half)
    half_vaccine_range = vaccine_collection.get(start, half)

    half_vaccine_list = list(half_vaccine_range)
    half_tweet_list = list(half_tweet_range)

    # display chart with data
    model = visualization.vaccination_twitter_plot(
        tweet_list, vaccine_list, 'Vaccination Rate As Related To'
                                  + ' Ongoing Twitter Discourse In The US',
        regression_twitter=half_tweet_list, regression_vaccine=half_vaccine_list)

    figures.append(visualization.unwrap_figure(model.to_html()))

    figures.append(visualization.text_block('These results are somewhat surprising,'
                                            + ' the data used to generate the model can'
                                            + ' be seen below.'))

    half_x = list(range(len(half_vaccine_list)))

    # half vaccine figure
    half_vaccine_fig = px.scatter(x=half_x, y=half_vaccine_list,
                                  title='Vaccination Rate Across US (Until Halfway Point)',
                                  labels=dict(x='Days Since 2021-02-28',
                                              y='Mean Daily Vaccinations Per State'))

    figures.append(visualization.unwrap_figure(half_vaccine_fig.to_html()))

    # half tweet figure
    half_tweet_fig = px.scatter(x=half_x, y=half_tweet_list,
                                title='Twitter Vaccine Perception Across US (Until Halfway Point)',
                                labels=dict(x='Days Since 2021-02-28', y='Mean VADER Score'))

    figures.append(visualization.unwrap_figure(half_tweet_fig.to_html()))

    figures.append(visualization.text_block(
        '<div style="text-align: center; font-size: 24pt; padding: 24pt">RAW DATA</div>'))

    figures.append(visualization.text_block(
        'Here is the raw data for the entire analysis (as opposed to the graphs above'
        + ' which were half the raw data, and were only used to generate the model in'
        + ' the section above).'))

    full_x = list(range(len(vaccine_list)))

    # vaccine figure
    vaccine_fig = px.scatter(x=full_x, y=vaccine_list,
                             title='Vaccination Rate Across US',
                             labels=dict(x='Days Since 2021-02-28',
                                         y='Mean Daily Vaccinations Per State'))

    figures.append(visualization.unwrap_figure(vaccine_fig.to_html()))

    # tweet figure
    tweet_fig = px.scatter(x=full_x, y=tweet_list,
                           title='Twitter Vaccine Perception Across US',
                           labels=dict(x='Days Since 2021-02-28', y='Mean VADER Score'))

    figures.append(visualization.unwrap_figure(tweet_fig.to_html()))

    visualization.output(figures, app.output_path, app.template_path)
