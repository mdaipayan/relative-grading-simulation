"""Statistical analysis suite for relative grading simulation results."""

from relative_grading.statistics.friedman import run_friedman_test
from relative_grading.statistics.pairwise import run_pairwise_tests
from relative_grading.statistics.bootstrap import paired_bootstrap_ci
from relative_grading.statistics.moderation import run_moderation_analysis
from relative_grading.statistics.diagnostics import compute_model_diagnostics

__all__ = [
    "run_friedman_test",
    "run_pairwise_tests",
    "paired_bootstrap_ci",
    "run_moderation_analysis",
    "compute_model_diagnostics",
]
