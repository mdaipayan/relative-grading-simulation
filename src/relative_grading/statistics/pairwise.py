"""Pairwise Wilcoxon signed-rank tests with Holm correction and effect sizes."""

from typing import List, Dict, Any, Tuple
import itertools
import numpy as np
import pandas as pd
from scipy import stats
from relative_grading.statistics.bootstrap import paired_bootstrap_ci


def holm_bonferroni(p_values: List[float]) -> List[float]:
    """Apply Holm-Bonferroni step-down correction to a list of p-values."""
    m = len(p_values)
    if m == 0:
        return []

    # Pair with original indices
    indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m

    cum_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed_p):
        multiplier = m - rank
        adj_p = min(1.0, multiplier * p)
        cum_max = max(cum_max, adj_p)
        adjusted[orig_idx] = cum_max

    return adjusted


def compute_rank_biserial_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Compute matched-pairs rank-biserial correlation from signed ranks."""
    d = x - y
    nonzero_d = d[d != 0]
    n = len(nonzero_d)
    if n == 0:
        return 0.0

    abs_d = np.abs(nonzero_d)
    ranks = stats.rankdata(abs_d)

    w_plus = np.sum(ranks[nonzero_d > 0])
    w_minus = np.sum(ranks[nonzero_d < 0])
    total_w = w_plus + w_minus

    if total_w == 0:
        return 0.0

    return float((w_plus - w_minus) / total_w)


def run_pairwise_tests(
    df_results: pd.DataFrame,
    metric: str = "mean_grid_stability",
    methods: List[str] = None,
    n_boot: int = 2000,
    seed: int = 42,
) -> pd.DataFrame:
    """Run pairwise Wilcoxon signed-rank tests across all pairs of methods.

    Parameters
    ----------
    df_results : pd.DataFrame
        Results dataframe with cell_id, method, and metric columns.
    metric : str, default='mean_grid_stability'
        Target metric for pairwise comparisons.
    methods : List[str], optional
        List of methods to compare.
    n_boot : int, default=2000
        Bootstrap resamples for 95% CI.
    seed : int, default=42
        Random seed for bootstrap.

    Returns
    -------
    pd.DataFrame
        Pairwise comparisons table.
    """
    if methods is None:
        methods = ["MeanSD", "Percentile", "MaxMin", "QFactor", "MedianMAD"]

    pivot = df_results.pivot(index="cell_id", columns="method", values=metric)[methods].dropna()

    records = []
    pairs = list(itertools.combinations(methods, 2))

    for m1, m2 in pairs:
        v1 = pivot[m1].values
        v2 = pivot[m2].values
        diff = v1 - v2

        mean_diff = float(np.mean(diff))
        std_diff = float(np.std(diff, ddof=1)) if len(diff) > 1 else 0.0
        cohen_dz = float(mean_diff / std_diff) if std_diff > 0 else 0.0

        # Wilcoxon test
        try:
            w_res = stats.wilcoxon(v1, v2, alternative="two-sided")
            raw_p = float(w_res.pvalue)
            w_stat = float(w_res.statistic)
        except Exception:
            raw_p = 1.0
            w_stat = 0.0

        r_biserial = compute_rank_biserial_correlation(v1, v2)
        ci_low, ci_high = paired_bootstrap_ci(diff, n_boot=n_boot, seed=seed)

        records.append({
            "metric": metric,
            "method_1": m1,
            "method_2": m2,
            "mean_diff": mean_diff,
            "ci_lower_95": ci_low,
            "ci_upper_95": ci_high,
            "cohen_dz": cohen_dz,
            "rank_biserial": r_biserial,
            "wilcoxon_stat": w_stat,
            "raw_p": raw_p,
        })

    # Apply Holm correction
    raw_ps = [r["raw_p"] for r in records]
    adj_ps = holm_bonferroni(raw_ps)
    for i, adj_p in enumerate(adj_ps):
        records[i]["holm_adjusted_p"] = adj_p

    return pd.DataFrame(records)
