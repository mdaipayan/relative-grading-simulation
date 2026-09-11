"""Relative grading methods package.

Implements the 5 frozen grading methods:
- M1: Mean-SD
- M2: Percentile (Type-7)
- M3: Max-Min (Fixed Distribution)
- M4: Q-Factor (Constrained)
- M5: Median-MAD (Robust)
"""

from relative_grading.methods.base import GradingMethod
from relative_grading.methods.mean_sd import MeanSD
from relative_grading.methods.percentile import Percentile
from relative_grading.methods.max_min import MaxMin
from relative_grading.methods.q_factor import QFactor
from relative_grading.methods.median_mad import MedianMAD

__all__ = [
    "GradingMethod",
    "MeanSD",
    "Percentile",
    "MaxMin",
    "QFactor",
    "MedianMAD",
]
