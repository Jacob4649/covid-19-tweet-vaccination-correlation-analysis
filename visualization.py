"""Module for displaying information in graphs and figures"""

from typing import Dict, List
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from pandas import DataFrame
import plotly.express as px
from app import App
import webbrowser


def vaccination_twitter_plot(twitter: List[float],
                             vaccine: List[int], title: str,
                             regression_twitter: List[float] = None,
                             regression_vaccine: List[int] = None) -> go.Figure:
    """Get a figure showing the relationship between
    the provided tweet and vaccine information, with the provided title

    Optionally, can provide regression twitter and vaccine info to
    calculate line of best fit with different data from plot data

    Preconditions:
        - len(twitter) == len(vaccine)
        - regression_twitter is None == regression_vaccine is None"""
    # calculate regression
    t, v = regression_twitter, regression_vaccine
    if regression_twitter is None and regression_vaccine is None:
        t = twitter
        v = vaccine
    regression = _calculate_regression(t, v)

    # calculate residuals (technically absolute value of residuals)

    predictions = [prediction[0] for prediction in
                   regression.predict(
        np.array(twitter).reshape(-1, 1))]

    residuals = [abs(predictions[i] - vaccine[i])
                 for i in range(len(predictions))]

    # calculate line of best fit

    base_x = min(twitter)
    end_x = max(twitter)

    base_y = regression.predict(np.array(base_x).reshape(-1, 1))[0][0]
    end_y = regression.predict(np.array(end_x).reshape(-1, 1))[0][0]

    # create figure

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=twitter,
        y=vaccine,
        name='Vaccine Rates',
        mode='markers'
    ))

    fig.add_trace(go.Scatter(
        x=twitter,
        y=residuals,
        name='Absolute Value Of Residuals',
        mode='markers'
    ))

    fig.add_trace(go.Scatter(
        x=[base_x, end_x],
        y=[base_y, end_y],
        name='Best Fit',
        mode='lines'
    ))

    # show data used to perform regression if it is different from graph data

    if regression_vaccine is not None \
            and regression_twitter is not None:

        fig.add_trace(go.Scatter(
            x=twitter,
            y=vaccine,
            name='Vaccine Rates For Model Data',
            mode='markers'
        ))

        fig.add_trace(go.Scatter(
            x=twitter,
            y=residuals,
            name='Absolute Value Of Residuals For Model Data',
            mode='markers'
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Daily Mean VADER Score',
        yaxis_title='Daily Mean Vaccination Rate',
        legend_title='Legend'
    )

    return fig


def chloropleth(values: Dict[str, float], title: str, value_name: str, app: App):
    """Return a cloropleth figure with the specified title, and value name
    showing some value for each state using a dictionary
    of state codes mapped to values. Takes the name of each state from app state bundle

    Preconditions:
        - every state code in values is in the app state's locations attribute"""
    array = [[key, values[key], app.location_code_lookup(
        key).name] for key in values]

    dataframe = DataFrame(array, columns=['Code', 'Value', 'State Name'])

    fig = px.choropleth(dataframe,
                        title=title,
                        locations='Code',
                        color='Value',
                        color_continuous_scale='spectral_r',
                        hover_name='State Name',
                        locationmode='USA-states',
                        labels={
                            'Value': value_name},
                        scope='usa')

    return fig


def _calculate_regression(twitter: List[float], vaccine: List[int]) -> LinearRegression:
    """Return a linear regression calculated with the input data"""
    # calculate regression

    x_array = np.array(twitter).reshape(-1, 1)
    y_array = np.array(vaccine).reshape(-1, 1)

    return LinearRegression().fit(x_array, y_array)


def _read_template(path: str) -> str:
    """Return the content of the html template file found
    at the specified path"""
    with open(path, encoding='utf-8') as template:
        return '\n'.join(template.readlines())


def _insert_into_template(insert: str, path: str) -> str:
    """Return the html template file at the specified path,
    with the body replaced by the specified insert"""
    return _read_template(path).replace('{INSERT FIGURES HERE}', insert)


def unwrap_figure(figure: str) -> str:
    """Return the html representation of a figure, without its enclosing body tags"""
    return figure.replace('<body>', '').replace('</body>', '')


def _write_output(output: str, path: str) -> None:
    """Write the specified html to the specified path
    """
    with open(path, 'w', encoding='utf-8') as file:
        file.write(output)


def text_block(text: str) -> str:
    """Return a string text block to add to an html file with the specified text"""
    return '<div style="text-align:center">' + text + '</div>'


def output(blocks: List[str], path: str, template_path: str) -> None:
    """Writes an html output file to the speicified path, 
    using the template from the specified template
    path. Inserts the specified blocks of text and
    figures represented by strings. Then opens the file."""
    internals = ''.join(blocks)
    body = _insert_into_template(internals, template_path)
    _write_output(body, path)
    webbrowser.open_new(f'file://{path}')
