"""Executable script for validating simulation reproduction against audited frozen values."""

import argparse
from pathlib import Path
import sys

# Ensure src is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
import yaml

from relative_grading.validation.frozen_values import compare_with_frozen_baseline
from relative_grading.statistics.friedman import run_friedman_test


def main():
    parser = argparse.ArgumentParser(description="Audit and validate simulation reproduction.")
    parser.add_argument("--primary-results", type=str, default="results/primary/primary_cell_results.parquet")
    parser.add_argument("--repro-config", type=str, default="config/reproducibility.yaml")
    args = parser.parse_args()

    prim_path = Path(args.primary_results)
    if not prim_path.exists():
        prim_path = prim_path.with_suffix(".csv")

    if not prim_path.exists():
        print(f"Error: Simulation results not found at {args.primary_results}")
        print("Please execute `python scripts/run_primary.py` first.")
        return

    df = pd.read_parquet(prim_path) if prim_path.suffix == ".parquet" else pd.read_csv(prim_path)

    n_cells = df["cell_id"].nunique()
    reps_per_cell = int(df["replications"].iloc[0]) if "replications" in df.columns else 1000
    methods_count = df["method"].nunique()

    # Calculate reproduced mean stability across methods
    overall_stab = df.groupby("method")["mean_grid_stability"].mean().to_dict()

    # Compute Friedman test
    friedman_res = run_friedman_test(df, metric="mean_grid_stability")

    # Audit comparison against frozen baseline
    audit = compare_with_frozen_baseline(
        reproduced_stability=overall_stab,
        friedman_chi2=friedman_res.chi_square,
        kendall_w=friedman_res.kendall_w,
        config_path=args.repro_config,
    )

    status_str = "PASS" if audit.all_passed else "FAIL"

    print("========================================")
    print("RELATIVE GRADING REPRODUCIBILITY AUDIT")
    print("========================================")
    print(f"Primary cells:              {n_cells:,}")
    print(f"Replications/cell:          {reps_per_cell:,}")
    print(f"Methods:                    {methods_count}")
    print("")
    for m in ["MeanSD", "Percentile", "MaxMin", "QFactor", "MedianMAD"]:
        m_short = {"MeanSD": "M1", "Percentile": "M2", "MaxMin": "M3", "QFactor": "M4", "MedianMAD": "M5"}[m]
        val = overall_stab.get(m, 0.0)
        exp = audit.frozen_stability[m]
        diff = audit.stability_differences[m]
        print(f"{m_short} ({m}) stability:     {val:.4f}  (Frozen: {exp:.4f}, diff: {diff:+.4f})")
    print("")
    print(f"Friedman chi-square:        {friedman_res.chi_square:.3f}  (Frozen: {audit.frozen_friedman_chi2:.3f})")
    print(f"Kendall W:                  {friedman_res.kendall_w:.3f}    (Frozen: {audit.frozen_kendall_w:.3f})")
    print("")
    print(f"STATUS: {status_str}")
    print("========================================")

    # Write audit report to file
    out_dir = Path("results/validation")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / "audit_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("========================================\n")
        f.write("RELATIVE GRADING REPRODUCIBILITY AUDIT\n")
        f.write("========================================\n")
        f.write(f"Primary cells:              {n_cells:,}\n")
        f.write(f"Replications/cell:          {reps_per_cell:,}\n")
        f.write(f"Methods:                    {methods_count}\n\n")
        for m in ["MeanSD", "Percentile", "MaxMin", "QFactor", "MedianMAD"]:
            m_short = {"MeanSD": "M1", "Percentile": "M2", "MaxMin": "M3", "QFactor": "M4", "MedianMAD": "M5"}[m]
            val = overall_stab.get(m, 0.0)
            exp = audit.frozen_stability[m]
            diff = audit.stability_differences[m]
            f.write(f"{m_short} ({m}) stability:     {val:.4f}  (Frozen: {exp:.4f}, diff: {diff:+.4f})\n")
        f.write(f"\nFriedman chi-square:        {friedman_res.chi_square:.3f}  (Frozen: {audit.frozen_friedman_chi2:.3f})\n")
        f.write(f"Kendall W:                  {friedman_res.kendall_w:.3f}    (Frozen: {audit.frozen_kendall_w:.3f})\n\n")
        f.write(f"STATUS: {status_str}\n")
        f.write("========================================\n")
    print(f"Audit report written to {report_file}")


if __name__ == "__main__":
    main()
