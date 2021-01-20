# Load modules
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import altair as alt
import numpy as np
import pandas as pd
from helper import rate

# disable Altair limits
alt.data_transformers.disable_max_rows()

# read-in obesity data
file = "data/processed/obesity-combo.csv"
ob = pd.read_csv(file)

# Instantiate the app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Top Countries"),
        html.Iframe(
            id="bar",
            style={"border-width": "0", "width": "100%", "height": "500px"},
        ),
        html.Iframe(
            id="time",
            style={"border-width": "0", "width": "100%", "height": "500px"},
        ),
        dcc.Slider(
            id="input_year",
            value=2016,
            min=1975,
            max=2016,
            step=5,
            included=False,
            marks={
                i: "Label {}".format(i) if i == 1 else str(i) for i in range(1975, 2017)
            },
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
    temp = ob_yr.groupby("country").sum("obese", "pop")
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


@app.callback(
    Output("time", "srcDoc"),
    Input("input_year_range", "value"),
    Input("input_sex", "value"),
    Input("input_highlight_country", "value"),
)
def plot_time(input_year_range, input_sex, input_highlight_country):
    # Create list of desired years
    year_range = list(range(input_year_range[0], input_year_range[1] + 1))

    # Aggregate for sex and year
    if len(input_sex) == 1:
        filter = ob["year"].isin(year_range) & ob["sex"].isin(input_sex)
        ob_yr = ob.loc[filter, :]
        ob_yr.loc[:, "obese_rate"] = ob_yr["obese"] / ob_yr["pop"]
    elif len(input_sex) == 2:
        ob_yr = ob.loc[ob["year"].isin(year_range), :]
        ob_yr = ob_yr.groupby(["country", "year"])[["obese", "pop"]].sum().reset_index()
        ob_yr.loc[:, "obese_rate"] = ob_yr["obese"] / ob_yr["pop"]
    else:
        pass

    # Create regional trends
    ob_region = (
        ob.groupby(
            ["region", "year"],
        )[["obese", "pop"]]
        .sum()
        .reset_index()
    )
    ob_region["obese_rate"] = ob_region["obese"] / ob_region["pop"]

    ob_world = (
        ob.groupby(
            ["year"],
        )[["obese", "pop"]]
        .sum()
        .reset_index()
    )
    ob_world["obese_rate"] = ob_world["obese"] / ob_world["pop"]
    ob_world["region"] = "World"

    ob_combined = ob_region.append(ob_world)

    # Create Labels
    title_label = input_highlight_country + " and Obesity"
    sub_label = str(input_year_range[0]) + "-" + str(input_year_range[1])

    # Add click object
    click = alt.selection_multi()

    # Create Plot
    country_time_chart = (
        alt.Chart(ob_yr, title=alt.TitleParams(text=title_label, subtitle=sub_label))
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "year:O",
                scale=alt.Scale(zero=False),
                title="Years",
                axis=alt.Axis(grid=False),
            ),
            y=alt.Y("obese_rate:Q", title="Obesity Rate"),
            color=alt.condition(
                # (alt.datum.country == input_highlight_country),
                click,
                "country",
                alt.value("lightgray"),
                legend=None,
            ),
            opacity=alt.condition(
                alt.datum.country == input_highlight_country,
                alt.value(1),
                alt.value(0.1),
            ),
            tooltip="country",
        )
        .interactive()
        .add_selection(click)
    )

    print(ob_combined.head())

    world_time_chart = (
        alt.Chart(ob_combined)
        .mark_line(opacity=0.3)
        .encode(
            x=alt.X(
                "year:O",
                scale=alt.Scale(zero=False),
                title="Years",
                axis=alt.Axis(grid=False),
            ),
            y=alt.Y("obese_rate", title="Obesity Rate"),
            color="region",
            opacity=alt.condition(
                alt.datum.region == "World", alt.value(1), alt.value(0.4)
            ),
            tooltip="region",
        )
        .interactive()
    )

    return (country_time_chart + world_time_chart).to_html()


def plot_factor():
    pass


if __name__ == "__main__":
    app.run_server(debug=True)
