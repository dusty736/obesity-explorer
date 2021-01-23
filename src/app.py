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


# @app.callback(
#     Output("qs_ts", "children"),
#     Input("input_year_range", "value"),
#     Input("input_sex", "value"),
#     Input("input_region", "value"),
#     Input("input_income", "value"),
# )
# def gen_qs_ts(year, sex, region, income):
#     return he.gen_query_string(year, sex, region, income)


# @app.callback(
#     Output("qs_bar", "children"),
#     Input("input_year", "value"),
#     Input("input_sex", "value"),
#     Input("input_region", "value"),
#     Input("input_income", "value"),
# )
# def gen_qs_bar(year, sex, region, income):
#     return he.gen_query_string(year, sex, region, income)


# app.layout = html.Div(
#     [
#         html.H1("Top Countries"),
#         html.Iframe(
#             id="bar",
#             srcDoc=None,
#             style={"border-width": "0", "width": "100%", "height": "500px"},
#         ),
#         html.Iframe(
#             id="plt_map",
#             srcDoc=None,
#             style={"border-width": "0", "width": "100%", "height": "500px"},
#         ),
#         dcc.Slider(
#             id="input_year",
#             value=2016,
#             min=1975,
#             max=2016,
#             step=5,
#             included=False,
#             marks={i: f"{str(i)}" for i in range(1975, 2017, 5)},
#         ),
#         dcc.RadioItems(
#             id="input_sex",
#             options=[
#                 {"label": sex, "value": sex} for sex in ["Male", "Female", "Both"]
#             ],
#             value="Both",
#             labelStyle={"display": "inline-block"},
#         ),
#         dcc.Dropdown(
#             id="input_region",
#             value=list(ob["region"].dropna().unique()),
#             multi=True,
#             options=[
#                 {"label": region, "value": region}
#                 for region in list(ob["region"].dropna().unique())
#             ],
#         ),
#         dcc.Dropdown(
#             id="input_regressor",
#             value="smoke",
#             multi=False,
#             options=[
#                 {"label": "Smoking Rate", "value": "smoke"},
#                 {"label": "Primary Education Completion Rate", "value": "primedu"},
#                 {"label": "Unemployment Rate", "value": "unemployed"},
#             ],
#         ),
#         dcc.Dropdown(
#             id="input_income",
#             value=list(ob["income"].dropna().unique()),
#             multi=True,
#             options=[
#                 {"label": income, "value": income}
#                 for income in list(ob["income"].dropna().unique())
#             ],
#         ),
#         dcc.Dropdown(
#             id="input_highlight_country",
#             value="Canada",
#             multi=True,
#             searchable=True,
#             options=[
#                 {"label": country, "value": country}
#                 for country in list(ob["country"].unique())
#             ],
#         ),
#         dcc.RangeSlider(
#             id="input_year_range",
#             value=[1975, 2016],
#             min=1975,
#             max=2016,
#             step=1,
#             marks={
#                 i: "{}".format(i) if i == 1 else str(i) for i in range(1975, 2017, 5)
#             },
#         ),
#         html.P(id="qs_bar"),
#         html.P(id="qs_ts"),
#     ]
# )

app.layout = dbc.Container(
    [
        html.H1("Obesity Dashboard"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Br(),
                        dcc.RadioItems(
                            id="input_sex",
                            options=[
                                {"label": sex, "value": sex}
                                for sex in ["Male", "Female", "Both"]
                            ],
                            value="Both",
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


def plot_time():
    pass


def plot_factor():
    pass


@app.callback(
    Output("combo_plot", "srcDoc"),
    Input("input_year", "value"),
    Input("input_year_range", "value"),
    Input("input_sex", "value"),
    Input("input_region", "value"),
    Input("input_income", "value"),
)
def plot_all(year, year_range, sex, region, income):
    # Create query strings
    query_string_bar = he.gen_query_string(year, sex, region, income)
    # query_string_ts = he.gen_query_string(year_range, sex, region, income)

    # Create plots
    bar_plot = plot_bar(query_string_bar)
    world_plot = plot_map(query_string_bar)
    # ts_plot = plot_time(query_string_ts)
    # factor_plot = plot_factor(query_string_bar)

    # Combine plots
    combo_plot = world_plot & bar_plot

    return combo_plot.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
