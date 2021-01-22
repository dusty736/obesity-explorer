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


def gen_query_string(year, sex, region, income):
    """Generates A Query String For Filtering

    Args:
        year ([list, int]): A two element containing the start and the end of a year range or a single integer indicating a year
        sex ([str]): One of 'Female', 'Male' or 'Both'
        region ([list]): A list of all the regions of the world to filter by
        income ([list]): A list of all the income groups to filter by

    Returns:
        [str]: A query string to be passed into a pandas query
    """

    filters = {
        "sex": sex_selection(sex),
        "year": list(range(year[0], year[1] + 1)) if type(year) == list else [year],
        "region": region,
        "income": income,
    }

    query = " & ".join(["{} in {}".format(k, v) for k, v in filters.items()])
    return query