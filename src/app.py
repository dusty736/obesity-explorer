# Load modules
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import altair as alt
import numpy as np
import pandas as pd
import helper as he
from vega_datasets import data

# disable Altair limits
alt.data_transformers.disable_max_rows()

# read-in obesity data
file = "data/processed/obesity-combo.csv"
ob = pd.read_csv(file)
ob = ob[ob["region"] != "Aggregates"]


# read-in the countries taxonomy
cy_ids = pd.read_csv("data/country-ids.csv").rename(columns={"world_bank": "country"})

# load the geojson data
geojson = alt.topo_feature(data.world_110m.url, "countries")

# Instantiate the app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# CSS Styles
css_dd = {
    "font-size": "smaller",
}

css_sources = {
    "font-size": "xx-small",
}

app.layout = dbc.Container(
    [
        html.H1("Obesity Dashboard"),
        html.P(
            dcc.Markdown(
                """
                Obesity has been an increasing medical concern across the world in the 
                21st century. It is a medical precursor to diseases such as diabetes, 
                heart diseases, high blood pressure and certain types of cancers.
                This dashboard allows you to explore trends, probe associations, and 
                discover other patterns related to this global epidemic.
                """
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Br(),
                        html.Label("Filter Sex: "),
                        dcc.RadioItems(
                            id="input_sex",
                            options=[
                                {"label": sex, "value": sex}
                                for sex in ["Male", "Female", "Both"]
                            ],
                            value="Both",
                            style=css_dd,
                            labelStyle={"display": "inline-block"},
                            inputStyle={"margin-left": "20px"},
                        ),
                        html.Br(),
                        html.Label("Filter Year: "),
                        dcc.Slider(
                            id="input_year",
                            value=2016,
                            min=1975,
                            max=2016,
                            step=1,
                            included=False,
                            marks={i: f"{str(i)}" for i in range(1975, 2017, 5)},
                        ),
                        html.Br(),
                        html.Label(
                            [
                                "Filter Region:",
                                dcc.Dropdown(
                                    id="input_region",
                                    value=list(ob["region"].dropna().unique()),
                                    multi=True,
                                    clearable=False,
                                    style=css_dd,
                                    options=[
                                        {"label": region, "value": region}
                                        for region in list(
                                            ob["region"].dropna().unique()
                                        )
                                    ],
                                ),
                            ]
                        ),
                        html.Br(),
                        html.Label("Filter Income Group: "),
                        dcc.Dropdown(
                            id="input_income",
                            value=list(ob["income"].dropna().unique()),
                            multi=True,
                            clearable=False,
                            style=css_dd,
                            options=[
                                {"label": income, "value": income}
                                for income in list(ob["income"].dropna().unique())
                            ],
                        ),
                        html.Br(),
                        html.Label("Select Secondary Variable: "),
                        dcc.Dropdown(
                            id="input_regressor",
                            value="smoke",
                            multi=False,
                            style=css_dd,
                            options=[
                                {"label": "Smoking Rate", "value": "smoke"},
                                {
                                    "label": "Primary Education Completion Rate",
                                    "value": "primedu",
                                },
                                {"label": "Unemployment Rate", "value": "unemployed"},
                            ],
                        ),
                        html.Br(),
                        html.Label("Select Grouping Variable: "),
                        dcc.Dropdown(
                            id="input_grouper",
                            value="none",
                            multi=False,
                            style=css_dd,
                            options=[
                                {"label": "Income group", "value": "income"},
                                {"label": "Sex", "value": "sex"},
                                {"label": "Region", "value": "region"},
                                {"label": "No grouping", "value": "none"},
                            ],
                        ),
                        html.Br(),
                        html.Label("Highlight Countries: "),
                        dcc.Dropdown(
                            id="input_highlight_country",
                            value="Canada",
                            multi=True,
                            searchable=True,
                            style=css_dd,
                            options=[
                                {"label": country, "value": country}
                                for country in list(ob["country"].unique())
                            ],
                        ),
                        html.Br(),
                        html.Label("Select Year Range: "),
                        dcc.RangeSlider(
                            id="input_year_range",
                            value=[1975, 2016],
                            min=1975,
                            max=2016,
                            step=1,
                            marks={
                                i: "{}".format(i) if i == 1 else str(i)
                                for i in range(1975, 2017, 5)
                            },
                        ),
                        html.Hr(),
                        html.P(
                            dcc.Markdown(
                                """
                                ##### Data Sources

                                The World Bank (n.d.). Indicators. https://data.worldbank.org/indicator. 
                                Retrieved January 16, 2021, from https://data.worldbank.org/indicator

                                World Health Organization(WHO) (n.d.). 
                                Prevalence of obesity among adults, BMI = 30 (age-standardized estimate) (%). 
                                Retrieved January 16, 2021, from 
                                https://www.who.int/data/gho/data/indicators/indicator-details/GHO/prevalence-of-obesity-among-adults-bmi-=-30-(age-standardized-estimate)-(-)


                                ---
                                This dashboard is created by [dusty736](https://github.com/dusty736), [tanmaysharma19](https://github.com/tanmaysharma19), [jraza19](https://github.com/jraza19), and [rtaph](https://github.com/rtaph). View the source code and contribute [here](https://github.com/UBC-MDS/obesity-explorer).
                                """
                            ),
                            style=css_sources,
                        ),
                    ],
                    md=4,
                    style={
                        "border": "1px solid #d3d3d3",
                        "border-radius": "10px",
                        "background-color": "rgba(220, 220, 220, 0.5)",
                    },
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                html.Iframe(
                                    id="combo_plot",
                                    srcDoc=None,
                                    style={
                                        "border-width": "0",
                                        "width": "100%",
                                        "height": "1250px",
                                    },
                                ),
                            ],
                        )
                    ]
                ),
            ],
        ),
        html.Br(),
    ]
)

# Bar plot
def plot_bar(query_string, year):
    """Function to create an altair bar plot of the top 10 countries

    Function to create an altair chart of the top 10 countries
    ordered based on obesity rate and disaggregated as per the
    user inputs received through the app dropdown filters.

    Args:
        query_string ([str]): string containing the attributes to be used in a pandas query
                               for filtering the data for the bar plot

        year ([float]): year

    Returns:
        [altair chart]: An altair bar plot of the top 10 countries
    """

    n = 10

    title_label = "Top " + str(n) + " Countries"
    sub_label = str(year)

    n = 10
    temp = he.make_rate_data(["country"], ["obese"], query_string)
    ob_sorted = temp.sort_values("obese", ascending=False).head(n).reset_index()
    chart = (
        alt.Chart(
            ob_sorted, title=alt.TitleParams(text=title_label, subtitle=sub_label)
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "obese",
                type="quantitative",
                title="Obesity Rate",
                scale=alt.Scale(domain=[0.1, 0.8]),
                axis=alt.Axis(format="%", grid=False),
            ),
            y=alt.Y("country", sort="-x", title=""),
            color="obese",
            tooltip=alt.Tooltip("obese:Q", format=".1%", title="Obesity Rate"),
        )
        .properties(width=450, height=150)
        .interactive()
    )
    return chart


# Map plot
def plot_map(query_string, year):

    """Fuction to create an altair chloropleth world map plot showing the global obesity rates

    Args:
        query_string ([str]): string containing the attributes to be used in a pandas query
                               for filtering the data for the bar plot

        year ([float]): year

    Returns:
        [altair chart]: An altair chloropleth world map plot showing the global obesity rates
    """

    title_label = "Obesity Rates"
    sub_label = str(year)

    df = (
        he.make_rate_data(["country"], ["obese"], query_string)
        .merge(cy_ids, "right", on="country")
        .sort_values("obese", ascending=False)
    )
    world = (
        (
            alt.Chart(
                geojson, title=alt.TitleParams(text=title_label, subtitle=sub_label)
            )
            .mark_geoshape()
            .transform_lookup(
                lookup="id",
                from_=alt.LookupData(df, "id", ["country", "obese"]),
            )
            .encode(
                color=alt.Color(
                    "obese:Q",
                    scale=alt.Scale(scheme="viridis"),
                    title="Obesity",
                    legend=alt.Legend(format=".0%"),
                ),
                stroke=alt.value("black"),
                tooltip=[
                    alt.Tooltip("country:N", title="Country"),
                    alt.Tooltip("obese:Q", format=".1%", title="Obesity Rate"),
                ],
            )
        )
        .project("naturalEarth1")
        .properties(width=450, height=300)
    )
    return world


# Time Series plot
def plot_time(query_string, highlight_country, year_range):

    """Function to create a time series plot showing the country-wise global obesity rates

    Function to create a time series(spaghetti) plot showing the global obesity rates
    for all the countries for a range of years as selected by the user

    Args:
        query_string ([str]): string containing the attributes to be used in a pandas query
                               for filtering the data for the bar plot

        highlight_country ([str]): name of the country to be highlighted in the time series plot

        year_range ([float]): range of years to be selected for the time series plot

    Returns:
        [altair chart]: An altair time series plot showing the country-wise global obesity rates
    """

    # Filter data
    ob_yr = he.make_rate_data(["country", "year"], ["obese"], query_string)

    # Create labels
    title_label = "World Obesity"
    sub_label = str(year_range[0]) + "-" + str(year_range[1])

    # Format country
    highlight_country = (
        [highlight_country] if type(highlight_country) == str else highlight_country
    )

    # Get data for highlighted countries
    highlighted_data = ob_yr[ob_yr["country"].isin(highlight_country)]
    highlighted_data.loc[:, "highlighted"] = [
        country if country in highlight_country else "other"
        for country in highlighted_data["country"]
    ]

    # Create chart
    country_time_chart = (
        alt.Chart(ob_yr, title=alt.TitleParams(text=title_label, subtitle=sub_label))
        .mark_line()
        .encode(
            x=alt.X(
                "year:O",
                scale=alt.Scale(zero=False),
                title="Years",
                axis=alt.Axis(grid=False),
            ),
            y=alt.Y(
                "obese:Q",
                title="Obesity Rate",
                axis=alt.Axis(format="%"),
            ),
            color=alt.condition(
                alt.Predicate(
                    alt.FieldOneOfPredicate(field="country", oneOf=highlight_country)
                ),
                "country",
                alt.value("lightgray"),
                # legend=None,
            ),
            opacity=alt.condition(
                alt.Predicate(
                    alt.FieldOneOfPredicate(field="country", oneOf=highlight_country)
                ),
                alt.value(1),
                alt.value(0.2),
            ),
            tooltip="country",
        )
        .properties(width=450, height=300)
        .interactive()
    )

    highlighted_time_chart = (
        alt.Chart(highlighted_data)
        .mark_line()
        .encode(
            x=alt.X(
                "year:O",
                scale=alt.Scale(zero=False),
                title="Years",
                axis=alt.Axis(grid=False),
            ),
            y=alt.Y(
                "obese:Q",
                title="Obesity Rate",
                axis=alt.Axis(format="%"),
            ),
            color=alt.Color(
                "highlighted",
                legend=alt.Legend(title="Countries", values=highlight_country),
            ),
            tooltip="country",
        )
    )

    # return country_time_chart
    return country_time_chart + highlighted_time_chart


# Scatter plot
def plot_factor(regressor, grouper, query_string):

    """Function to create a scatter plot showing the association of obesity rate vs other factors

    Function to create a scatter plot showing the association of obesity rate
    vs other factors and grouped by different aggregators as selected by the user
    through the different dropdown filters.

    Args:
        regressor ([str]): the regressor to be used in the scatter plot

        grouper ([str]): the attribute to be used for grouping the data in the scatter plot

        query_string ([str]): string containing the attributes to be used in a pandas query
                               for filtering the data for the bar plot

    Returns:
        [altair chart]: An altair scatter plot showing the association of obesity rate vs other factors
    """

    label_dict = {
        "primedu": "Primary Education Completion Rate",
        "smoke": "Smoking Rate",
        "unemployed": "Unemployment Rate",
        "income": "Income Group",
        "sex": "Sex",
        "region": "Region",
    }

    title_label = "Obesity Rate vs " + label_dict[regressor]
    sub_label = "" if grouper == "none" else "by " + label_dict[grouper]

    temp = he.make_rate_data(
        ["country", grouper], ["primedu", "smoke", "unemployed", "obese"], query_string
    )

    chart = (
        alt.Chart(temp, title=alt.TitleParams(text=title_label, subtitle=sub_label))
        .mark_circle(opacity=0.25)
        .encode(
            x=alt.X(
                regressor,
                type="quantitative",
                title=label_dict[regressor],
                axis=alt.Axis(format="%", grid=False),
            ),
            y=alt.Y(
                "obese", title="Obesity Rate", axis=alt.Axis(format="%", grid=False)
            ),
            color=alt.Color(grouper, type="nominal", title="Legend"),
            tooltip=[
                alt.Tooltip("country:N", title="Country"),
                alt.Tooltip(grouper, title="Grouping Variable"),
                alt.Tooltip("obese:Q", format=".1%", title="Obesity Rate"),
            ],
        )
        .properties(width=450, height=150)
        .interactive()
    )

    factor_chart = chart

    return factor_chart


@app.callback(
    Output("combo_plot", "srcDoc"),
    Input("input_year", "value"),
    Input("input_year_range", "value"),
    Input("input_sex", "value"),
    Input("input_region", "value"),
    Input("input_highlight_country", "value"),
    Input("input_income", "value"),
    Input("input_regressor", "value"),
    Input("input_grouper", "value"),
)
def plot_all(
    year, year_range, sex, region, highlight_country, income, regressor, grouper
):

    """Function to combine all the different plots generated for the dashboard

    Args:
        year ([int]): year

        year_range ([list]): range of years to be selected for the time series plot

        sex ([list]): sex

        region ([list]): region

        highlight_country ([list]): name of the country to be highlighted in the time series plot

        income ([list]): income atribute in the data

        regressor ([str]): the regressor to be used in the scatter plot

        grouper ([str]): the attribute to be used for grouping the data in the scatter plot

    Returns:
        [altair chart]: An altair combination plot showing 4 charts: bar plot, chloropleth, time series, and scatter plot
    """
    # Create query strings
    query_string_bar = he.gen_query_string(year, sex, region, income)
    query_string_ts = he.gen_query_string(year_range, sex, region, income)

    # Create plots
    bar_plot = plot_bar(query_string_bar, year)
    world_plot = plot_map(query_string_bar, year)
    ts_plot = plot_time(query_string_ts, highlight_country, year_range)
    factor_plot = plot_factor(regressor, grouper, query_string_bar)

    # Combine plots
    combo_plot = (ts_plot & factor_plot) & (world_plot & bar_plot)

    return combo_plot.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
