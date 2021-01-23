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
# app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# CSS Styles
css_dd = {
    "font-size": "smaller",
}

app.layout = dbc.Container(
    [
        html.H1("Obesity Dashboard"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Br(),
                        html.Label("Sex: "),
                        dcc.RadioItems(
                            id="input_sex",
                            options=[
                                {"label": sex, "value": sex}
                                for sex in ["Male", "Female", "Both"]
                            ],
                            value="Both",
                            style=css_dd,
                            labelStyle={"display": "inline-block"},
                        ),
                        html.Br(),
                        dcc.Slider(
                            id="input_year",
                            value=2016,
                            min=1975,
                            max=2016,
                            step=5,
                            included=False,
                            marks={i: f"{str(i)}" for i in range(1975, 2017, 5)},
                        ),
                        html.Br(),
                        html.Label(
                            [
                                "Region",
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
                                        "height": "750px",
                                    },
                                ),
                                html.Iframe(
                                    id="time",
                                    srcDoc=None,
                                    style={
                                        "border-width": "0",
                                        "width": "100%",
                                        "height": "400px",
                                    },
                                ),
                            ],
                        )
                    ]
                ),
            ],
        ),
    ]
)


# Bar plot
# @app.callback(Output("bar", "srcDoc"), Input("qs_bar", "children"))
def plot_bar(query_string):
    n = 10
    temp = he.make_rate_data(["country"], ["obese"], query_string)
    ob_sorted = temp.sort_values("obese", ascending=False).head(n).reset_index()
    chart = (
        alt.Chart(ob_sorted)
        .mark_bar()
        .encode(
            x=alt.X("obese", type="quantitative", title="Obesity Rate"),
            y=alt.Y("country", sort="x", title="Country"),
            color="obese",
            tooltip="obese",
        )
        .properties(width=450, height=150)
        .interactive()
    )
    return chart


# @app.callback(Output("plt_map", "srcDoc"), Input("qs_bar", "children"))
def plot_map(query_string):
    df = (
        he.make_rate_data(["country"], ["obese"], query_string)
        .merge(cy_ids, "right", on="country")
        .sort_values("obese", ascending=False)
    )
    world = (
        (
            alt.Chart(geojson)
            .mark_geoshape()
            .transform_lookup(
                lookup="id",
                from_=alt.LookupData(df, "id", ["country", "obese"]),
            )
            .encode(
                color=alt.Color("obese:Q", scale=alt.Scale(scheme="viridis")),
                # opacity=alt.condition(map_click, alt.value(1), alt.value(0.2)),
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


def plot_time(query_string, highlight_country, year_range):

    # Filter data
    ob_yr = he.make_rate_data(["country", "year"], ["obese"], query_string)

    # Create labels
    # title_label = highlight_country + " and Obesity"
    title_label = "World Obesity"
    sub_label = str(year_range[0]) + "-" + str(year_range[1])

    # Add click object
    # click = alt.selection_multi()

    # Format country
    highlight_country = (
        [highlight_country] if type(highlight_country) == str else highlight_country
    )

    # Create chart
    alt.renderers.set_embed_options(
        padding={"left": 0, "right": 0, "bottom": 0, "top": 0}
    )

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
                legend=None,
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
        .properties(width=400, height=300)
        .interactive()
        # .add_selection(click)
    )

    return country_time_chart


def plot_factor():
    pass


@app.callback(
    Output("combo_plot", "srcDoc"),
    Input("input_year", "value"),
    Input("input_year_range", "value"),
    Input("input_sex", "value"),
    Input("input_region", "value"),
    Input("input_highlight_country", "value"),
    Input("input_income", "value"),
)
def plot_all(year, year_range, sex, region, highlight_country, income):
    # Create query strings
    query_string_bar = he.gen_query_string(year, sex, region, income)
    query_string_ts = he.gen_query_string(year_range, sex, region, income)

    # Create plots
    bar_plot = plot_bar(query_string_bar)
    world_plot = plot_map(query_string_bar)
    ts_plot = plot_time(query_string_ts, highlight_country, year_range)
    # factor_plot = plot_factor(query_string_bar)

    # Combine plots
    combo_plot = ts_plot | (world_plot & bar_plot)

    return combo_plot.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
