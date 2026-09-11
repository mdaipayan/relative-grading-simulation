"""Unit tests for primary and secondary metric calculations."""

import numpy as np
import pytest
from relative_grading.metrics import (
    calculate_grid_metrics,
    calculate_boundary_metrics,
    calculate_secondary_metrics,
)


def test_perfect_stability():
    # If all replications assign the exact same grade to every grid point, stability should be 1.0
    r = 100
    grid_size = 101
    rep_grades = np.full((r, grid_size), 3, dtype=int)
    ref_grades = np.full(grid_size, 3, dtype=int)

    stab, disag, pt_stab, pt_disag = calculate_grid_metrics(rep_grades, ref_grades)
    assert np.isclose(stab, 1.0)
    assert np.isclose(disag, 0.0)


def test_boundary_displacement_and_rmse():
    r = 10
    # True boundaries
    ref_b = np.array([80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0])
    # Shifted by +2.0 across all boundaries
    rep_b = np.tile(ref_b + 2.0, (r, 1))

    disp, rmse = calculate_boundary_metrics(rep_b, ref_b)
    assert np.isclose(disp, 2.0)
    assert np.isclose(rmse, 2.0)


def test_secondary_metrics():
    r = 20
    n = 10
    cohort_grades = np.random.randint(1, 8, size=(r, n))
    cohort_ext = np.full((r, n), 25.0)
    cohort_tot = np.full((r, n), 55.0)
    native_b7 = np.full(r, 20.0)
    ce = 20.0

    p_mean, p_sd, gc_sd, override_rate = calculate_secondary_metrics(
        cohort_grades=cohort_grades,
        cohort_external=cohort_ext,
        cohort_total=cohort_tot,
        native_b7=native_b7,
        ce=ce,
    )
    assert 0.0 <= p_mean <= 1.0
    assert p_sd >= 0.0
    assert override_rate == 0.0  # since external is 25.0 >= CE (no override)
