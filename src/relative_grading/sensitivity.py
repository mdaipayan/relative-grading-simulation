"""Focused rho sensitivity experiment engine (Step 8B).

Frozen design (Section 16):
- rho in {0.0, 0.3, 0.6, 0.8, 0.9}
- CE = 20.0
- 3 contamination conditions: clean, 5% lower, 5% upper
- 10 cohort sizes
- 6 distributions
- 180 cells per rho -> 900 cells total
- R = 500 per cell
"""

from typing import List, Dict, Any
from relative_grading.simulation import CellSpec, run_cell_simulation
from relative_grading.reference import ReferenceCohortManager


def build_rho_sensitivity_cell_grid(
    cohort_sizes: List[int],
    distributions: List[str],
    rho_values: List[float],
    ce: float = 20.0,
) -> List[CellSpec]:
    """Construct the 900-cell rho sensitivity experimental design."""
    cells: List[CellSpec] = []
    cell_id = 0

    contam_specs = [
        (0.0, "clean"),
        (0.05, "lower"),
        (0.05, "upper"),
    ]

    for rho in rho_values:
        for n in cohort_sizes:
            for dist in distributions:
                for eps, direction in contam_specs:
                    cells.append(
                        CellSpec(
                            cell_id=cell_id,
                            n=n,
                            distribution=dist,
                            ce=ce,
                            epsilon=eps,
                            direction=direction,
                            rho=rho,
                        )
                    )
                    cell_id += 1

    return cells
