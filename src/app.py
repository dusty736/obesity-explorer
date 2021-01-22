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
            marks={i: f"Label {str(i)}" for i in range(1975, 2017)},
        ),
        dcc.Checklist(
            id="input_sex",
            options=[{"label": sex, "value": sex} for sex in ["Male", "Female"]],
            value=["Male", "Female"],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Dropdown(
            id="input_region",
            value=list(ob["region"].unique()),
            multi=True,
            options=[
                {"label": region, "value": region}
                for region in list(ob["region"].unique())
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
                i: "Label {}".format(i) if i == 1 else str(i)
                for i in range(1975, 2017, 5)
            },
        ),
    ]
)


# Bar plot
@app.callback(Output("bar", "srcDoc"), Input("input_year", "value"))
def plot_bar(year=0, n=20):
    ob_yr = ob.loc[ob["year"] == year, :]
    temp = ob_yr.groupby("country")[["obese", "pop"]].sum()
    temp["ob_rate"] = temp["obese"] / temp["pop"]
    ob_sorted = temp.sort_values("ob_rate", ascending=False).head(n).reset_index()
    chart = (
        alt.Chart(ob_sorted)
        .mark_bar()
        .encode(
            x=alt.X("ob_rate", type="quantitative", title="Obesity Rate"),
            y=alt.Y("country", sort="x", title="Country"),
            color="ob_rate",
            tooltip="ob_rate",
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
