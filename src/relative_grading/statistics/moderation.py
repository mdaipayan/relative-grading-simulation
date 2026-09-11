"""Moderation analysis module using statsmodels OLS with HC3 robust covariance.

Model (Section 17):
For M4 minus each comparator (M1, M2, M3, M5):
diff ~ C(N)
     + C(Distribution)
     + C(CE)
     + C(Contamination)
     + C(N):C(Contamination)
     + C(Distribution):C(Contamination)
     + C(CE):C(Contamination)
Fitted with HC3 robust standard errors.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from relative_grading.statistics.diagnostics import compute_model_diagnostics, RegressionDiagnostics


def run_moderation_analysis(
    df_results: pd.DataFrame,
    comparators: List[str] = None,
    metric: str = "mean_grid_stability",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fit factorial moderation models for (M4 - comparator) using HC3 robust standard errors.

    Parameters
    ----------
    df_results : pd.DataFrame
        Cell-level simulation results dataframe.
    comparators : List[str], optional
        List of comparator methods to test against QFactor (default: MeanSD, Percentile, MaxMin, MedianMAD).
    metric : str, default='mean_grid_stability'
        Target outcome metric.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (coefficients_table, diagnostics_table)
    """
    if comparators is None:
        comparators = ["MeanSD", "Percentile", "MaxMin", "MedianMAD"]

    # Pivot to get method columns
    wide = df_results.pivot(
        index=["cell_id", "N", "distribution", "CE", "epsilon", "direction"],
        columns="method",
        values=metric,
    ).reset_index()

    # Combine epsilon and direction into Contamination factor
    wide["Contamination"] = wide["epsilon"].astype(str) + "_" + wide["direction"].astype(str)

    formula = (
        "diff ~ C(N) + C(distribution) + C(CE) + C(Contamination) "
        "+ C(N):C(Contamination) + C(distribution):C(Contamination) + C(CE):C(Contamination)"
    )

    all_coefs = []
    all_diags = []

    for comp in comparators:
        if comp not in wide.columns or "QFactor" not in wide.columns:
            continue

        wide["diff"] = wide["QFactor"] - wide[comp]

        # Fit with HC3 robust standard errors
        try:
            model = smf.ols(formula, data=wide)
            fit_hc3 = model.fit(cov_type="HC3")

            # Diagnostics
            diag = compute_model_diagnostics(fit_hc3)
            all_diags.append({
                "comparator": comp,
                "metric": metric,
                "r_squared": diag.r_squared,
                "adj_r_squared": diag.adj_r_squared,
                "breusch_pagan_stat": diag.breusch_pagan_stat,
                "breusch_pagan_p": diag.breusch_pagan_p,
                "residual_skew": diag.residual_skewness,
                "residual_excess_kurtosis": diag.residual_excess_kurtosis,
                "max_cooks_distance": diag.max_cooks_distance,
            })

            # Coefficients
            params = fit_hc3.params
            bse = fit_hc3.bse
            tvalues = fit_hc3.tvalues
            pvalues = fit_hc3.pvalues
            conf_int = fit_hc3.conf_int()

            for term in params.index:
                all_coefs.append({
                    "comparator": comp,
                    "term": term,
                    "coef": float(params[term]),
                    "std_err_hc3": float(bse[term]) if hasattr(bse, "__getitem__") else float(bse),
                    "t_stat": float(tvalues[term]) if hasattr(tvalues, "__getitem__") else float(tvalues),
                    "p_value": float(pvalues[term]) if hasattr(pvalues, "__getitem__") else float(pvalues),
                    "ci_lower_95": float(conf_int.loc[term, 0]),
                    "ci_upper_95": float(conf_int.loc[term, 1]),
                })
        except Exception as e:
            # Handle cases where sample size is smaller than design matrix (e.g. test runs)
            all_diags.append({
                "comparator": comp,
                "metric": metric,
                "r_squared": np.nan,
                "adj_r_squared": np.nan,
                "breusch_pagan_stat": np.nan,
                "breusch_pagan_p": np.nan,
                "residual_skew": np.nan,
                "residual_excess_kurtosis": np.nan,
                "max_cooks_distance": np.nan,
                "error": str(e),
            })

    return pd.DataFrame(all_coefs), pd.DataFrame(all_diags)
