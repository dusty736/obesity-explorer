# Load modules
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import altair as alt
from vega_datasets import data
import numpy as np
import pandas as pd

# disable Altair limits
alt.data_transformers.disable_max_rows()

# read-in obesity data
file = "data/processed/obesity-combo.csv"
ob = pd.read_csv(file)

# Instantiate the app
app = dash.Dash(__name__)


# Scatter plot
def plot_altair(xmax=0):
    ob_sub = ob.loc[ob["year"] == xmax, :]
    rates = (
        ob_sub.groupby(["region", "country"])["obese", "smoke", "pop"]
        .sum()
        .reset_index()
    ).dropna()
    rates["smoker_rate"] = rates["smoke"] / rates["pop"]
    rates["obesity_rate"] = rates["obese"] / rates["pop"]
    chart = (
        alt.Chart(rates, title=f"Obesity vs. Smoking in {xmax}")
        .mark_point()
        .encode(
            alt.X("smoker_rate", title="Smoking Rate"),
            alt.Y("obesity_rate", title="Obesity Rate"),
            alt.Color("region", title="Region"),
            tooltip="country",
        )
        .interactive()
    )
    return chart.to_html()


app.layout = html.Div(
    [
        html.H1("Obesity Explorer"),
        html.Iframe(
            id="scatter",
            srcDoc=plot_altair(),
            style={"border-width": "0", "width": "100%", "height": "400px"},
        ),
        html.H4("Select a year:"),
        dcc.Slider(
            id="xslider",
            min=2007,
            max=2016,
            value=2016,
            step=1,
            marks={
                i: "Label {}".format(i) if i == 1 else str(i) for i in range(2007, 2017)
            },
        ),
    ]
)


@app.callback(Output("scatter", "srcDoc"), Input("xslider", "value"))
def update_output(xmax):
    return plot_altair(xmax)


if __name__ == "__main__":
    app.run_server(debug=True)
