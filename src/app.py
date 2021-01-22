# Load modules
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import altair as alt
import numpy as np
import pandas as pd
import helper as he

# disable Altair limits
alt.data_transformers.disable_max_rows()

# read-in obesity data
file = "data/processed/obesity-combo.csv"
ob = pd.read_csv(file)

# Instantiate the app
app = dash.Dash(__name__)

server = app.server


@app.callback(
    Output("teststring", "children"),
    Input("input_year", "value"),
    Input("input_sex", "value"),
)
def gen_query_string(year, sex):
    filters = {
        "sex": he.sex_selection(sex),
        "year": [year],
    }

    query = " & ".join(["{} in {}".format(k, v) for k, v in filters.items()])
    return query


app.layout = html.Div(
    [
        html.H1("Top Countries"),
        html.Iframe(
            id="bar",
            srcDoc=None,
            style={"border-width": "0", "width": "100%", "height": "500px"},
        ),
        dcc.Slider(
            id="input_year",
            value=2016,
            min=1975,
            max=2016,
            step=5,
            included=False,
            marks={i: f"{str(i)}" for i in range(1975, 2017, 5)},
        ),
        dcc.RadioItems(
            id="input_sex",
            options=[
                {"label": sex, "value": sex} for sex in ["Male", "Female", "Both"]
            ],
            value="Both",
            labelStyle={"display": "inline-block"},
        ),
        dcc.Dropdown(
            id="input_region",
            value=list(ob["region"].unique()),
            multi=True,
            options=[
                {"label": region, "value": region}
                for region in list(ob["region"].dropna().unique())
            ],
        ),
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
        dcc.RangeSlider(
            id="input_year_range",
            value=[1975, 2016],
            min=1975,
            max=2016,
            step=1,
            marks={
                i: "{}".format(i) if i == 1 else str(i) for i in range(1975, 2017, 5)
            },
        ),
        html.P(id="teststring"),
    ]
)


# Bar plot
@app.callback(Output("bar", "srcDoc"), Input("teststring", "children"))
def plot_bar(q):
    n = 20
    temp = he.make_rate_data(["country"], ["obese"], q)
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
        .interactive()
    )
    return chart.to_html()


def plot_map():
    pass


def plot_time():
    pass


def plot_factor():
    pass


if __name__ == "__main__":
    app.run_server(debug=True)
