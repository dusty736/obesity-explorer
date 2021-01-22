# utilities/helper functions for dashboard

import pandas as pd


def sex_selection(input):
    """Return Sex Input Variable as a List"""
    return ["Male", "Female"] if input == "Both" else [input]


# read-in obesity data
file = "data/processed/obesity-combo.csv"
ob = pd.read_csv(file)


def make_rate_data(grp, valuevars, query="none == 'All'", data=ob):
    """Filters, Groups, and Calculates Rates

    Params:
        grp [list]: A list detailing the names of the variables to group by.
        valuevars [list]: A list detailing the names of the quantitative
            variable summarise and calculate a rate for (as a function of
            population).
        query [string]: A query string used to subset the data prior to
            aggregation.
        data [pd.DataFrame]: The obesity dataset.

    Returns:
        [pd.DataFrame]: A pandas data frame containing the grouping variables
            and rates for the value variables (carrying the same column name).
            Cells where a rate could not be calculated due to missing information
            are return as np.NaN.

    """
    grp_plus = grp + ["none"]

    ratedata = (
        data.query(query)
        .loc[:, grp + ["pop"] + valuevars]
        .melt(id_vars=grp + ["pop"], var_name="variable", value_name="value")
        .dropna()
        .groupby(grp + ["variable"])[["pop", "value"]]
        .sum()
        .reset_index()
        .assign(rate=lambda x: x["value"] / x["pop"])
        .drop(columns=["value", "pop"])
        .pivot(index=grp, columns="variable", values="rate")
        .reset_index()
    )
    return ratedata
