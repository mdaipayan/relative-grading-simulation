"""Regression diagnostics module for factorial moderation models."""

from dataclasses import dataclass
from typing import Dict, Any
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan


@dataclass(frozen=True)
class RegressionDiagnostics:
    """Container for regression diagnostic indicators."""
    r_squared: float
    adj_r_squared: float
    breusch_pagan_stat: float
    breusch_pagan_p: float
    residual_skewness: float
    residual_excess_kurtosis: float
    max_cooks_distance: float


def compute_model_diagnostics(model_fit) -> RegressionDiagnostics:
    """Compute standard regression diagnostics for an OLS fitted model.

    Parameters
    ----------
    model_fit : statsmodels OLSResults
        Fitted statsmodels OLS regression results.

    Returns
    -------
    RegressionDiagnostics
        Diagnostics containing R2, adjusted R2, BP test, skew, kurtosis, and Cook's D.
    """
    resid = model_fit.resid
    r2 = float(model_fit.rsquared)
    adj_r2 = float(model_fit.rsquared_adj)

    # Breusch-Pagan test for heteroscedasticity
    try:
        bp_stat, bp_p, _, _ = het_breuschpagan(resid, model_fit.model.exog)
    except Exception:
        bp_stat, bp_p = np.nan, np.nan

    # Residual distribution moments
    skew = float(stats.skew(resid))
    kurt = float(stats.kurtosis(resid, fisher=True))  # Fisher excess kurtosis (normal = 0)

    # Cook's distance
    try:
        influence = model_fit.get_influence()
        cooks_d = influence.cooks_distance[0]
        max_cooks = float(np.max(cooks_d))
    except Exception:
        max_cooks = np.nan

    return RegressionDiagnostics(
        r_squared=r2,
        adj_r_squared=adj_r2,
        breusch_pagan_stat=float(bp_stat),
        breusch_pagan_p=float(bp_p),
        residual_skewness=skew,
        residual_excess_kurtosis=kurt,
        max_cooks_distance=max_cooks,
    )
