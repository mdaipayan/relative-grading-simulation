"""Aggregation and summarization of cell-level simulation outputs."""

from typing import Dict, Any
import pandas as pd


def aggregate_primary_summaries(df_results: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generate manuscript summary tables by experimental factor.

    Parameters
    ----------
    df_results : pd.DataFrame
        Cell-level simulation results dataframe.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of aggregated summary dataframes.
    """
    summaries = {}

    # 1. Overall method performance
    overall = (
        df_results.groupby("method")[
            [
                "mean_grid_stability",
                "reference_disagreement",
                "mean_boundary_displacement",
                "boundary_rmse",
                "pass_rate_mean",
                "pass_rate_sd",
                "grade_count_sd_mean",
                "competency_override_rate",
            ]
        ]
        .mean()
        .reset_index()
    )
    summaries["overall_summary"] = overall

    # 2. By Cohort Size N
    by_n = (
        df_results.groupby(["N", "method"])["mean_grid_stability"]
        .mean()
        .unstack(level="method")
        .reset_index()
    )
    summaries["by_cohort_size"] = by_n

    # 3. By Distribution
    by_dist = (
        df_results.groupby(["distribution", "method"])["mean_grid_stability"]
        .mean()
        .unstack(level="method")
        .reset_index()
    )
    summaries["by_distribution"] = by_dist

    # 4. By Competency Threshold CE
    by_ce = (
        df_results.groupby(["CE", "method"])["mean_grid_stability"]
        .mean()
        .unstack(level="method")
        .reset_index()
    )
    summaries["by_ce"] = by_ce

    # 5. By Contamination level epsilon
    by_eps = (
        df_results.groupby(["epsilon", "method"])["mean_grid_stability"]
        .mean()
        .unstack(level="method")
        .reset_index()
    )
    summaries["by_contamination"] = by_eps

    # 6. By Contamination Direction
    by_dir = (
        df_results.groupby(["direction", "method"])["mean_grid_stability"]
        .mean()
        .unstack(level="method")
        .reset_index()
    )
    summaries["by_direction"] = by_dir

    return summaries
