"""Omnibus non-parametric Friedman test module across 5 grading methods."""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class FriedmanResult:
    """Results of omnibus Friedman test across methods."""
    chi_square: float
    p_value: float
    kendall_w: float
    n_cells: int
    k_methods: int
    mean_ranks: Dict[str, float]


def run_friedman_test(
    df_results: pd.DataFrame,
    metric: str = "mean_grid_stability",
    methods: List[str] = None,
) -> FriedmanResult:
    """Compute Friedman test across methods paired by cell_id.

    Parameters
    ----------
    df_results : pd.DataFrame
        DataFrame with columns ['cell_id', 'method', metric].
    metric : str, default='mean_grid_stability'
        Metric column to test.
    methods : List[str], optional
        Ordered list of method names. Default: MeanSD, Percentile, MaxMin, QFactor, MedianMAD.

    Returns
    -------
    FriedmanResult
        Chi-square statistic, p-value, Kendall's W, and mean method ranks.
    """
    if methods is None:
        methods = ["MeanSD", "Percentile", "MaxMin", "QFactor", "MedianMAD"]

    pivot = df_results.pivot(index="cell_id", columns="method", values=metric)[methods].dropna()
    n_cells, k_methods = pivot.shape

    # scipy friedman test
    arrays = [pivot[m].values for m in methods]
    stat_res = stats.friedmanchisquare(*arrays)
    chi2 = float(stat_res.statistic)
    p_val = float(stat_res.pvalue)

    # Kendall's W = chi2 / (N * (k - 1))
    kendall_w = float(chi2 / (n_cells * (k_methods - 1)))

    # Compute mean ranks
    # Higher stability should receive better rank (or rank from lowest to highest)
    ranks = pivot.rank(axis=1, ascending=False)
    mean_ranks = {m: float(ranks[m].mean()) for m in methods}

    return FriedmanResult(
        chi_square=chi2,
        p_value=p_val,
        kendall_w=kendall_w,
        n_cells=n_cells,
        k_methods=k_methods,
        mean_ranks=mean_ranks,
    )
