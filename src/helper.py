# utilities/helper functions for dashboard

import pandas as pd


def rate(x, y):
    """Safely calculates the rate of x and y

    Calculates the rate of x/y where both x and y are not missing

    Args:
        x ([Series]): any numeric series
        y ([Series]): any numeric series

    Returns:
        [float]: rate
    """
    condition = x.isna() | y.isna()
    return sum(x.loc[~condition]) / sum(y.loc[~condition])


rate(pd.Series([1, 2]), pd.Series([1, 2]))
