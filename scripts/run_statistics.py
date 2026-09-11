"""Executable script for running statistical analyses and generating tables."""

import argparse
from pathlib import Path
import sys

# Ensure src is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from relative_grading.statistics.friedman import run_friedman_test
from relative_grading.statistics.pairwise import run_pairwise_tests
from relative_grading.statistics.moderation import run_moderation_analysis


def main():
    parser = argparse.ArgumentParser(description="Run statistical analyses on simulation results.")
    parser.add_argument("--input", type=str, default="results/primary/primary_cell_results.parquet")
    parser.add_argument("--output-dir", type=str, default="results/statistical_analysis")
    parser.add_argument("--metric", type=str, default="mean_grid_stability")
    parser.add_argument("--n-boot", type=int, default=2000)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    in_path = Path(args.input)
    if not in_path.exists():
        # Fallback to CSV if parquet not yet generated
        csv_path = in_path.with_suffix(".csv")
        if csv_path.exists():
            in_path = csv_path
        else:
            raise FileNotFoundError(f"Simulation results not found at {args.input}")

    if in_path.suffix == ".parquet":
        df = pd.read_parquet(in_path)
    else:
        df = pd.read_csv(in_path)

    print(f"Loaded {len(df)} records from {in_path}")

    # 1. Omnibus Friedman test
    print("Running Omnibus Friedman test...")
    friedman_res = run_friedman_test(df, metric=args.metric)
    df_friedman = pd.DataFrame([{
        "chi_square": friedman_res.chi_square,
        "p_value": friedman_res.p_value,
        "kendall_w": friedman_res.kendall_w,
        "n_cells": friedman_res.n_cells,
        "k_methods": friedman_res.k_methods,
        **{f"rank_{m}": r for m, r in friedman_res.mean_ranks.items()},
    }])
    df_friedman.to_csv(out_dir / "friedman.csv", index=False)
    print(f"Friedman Chi-square = {friedman_res.chi_square:.4f}, Kendall's W = {friedman_res.kendall_w:.4f}")

    # 2. Pairwise Wilcoxon tests with Holm correction
    print("Running Pairwise Wilcoxon tests with Holm correction & bootstrap CIs...")
    df_pairwise = run_pairwise_tests(df, metric=args.metric, n_boot=args.n_boot)
    df_pairwise.to_csv(out_dir / "pairwise.csv", index=False)

    # Save dedicated bootstrap table as specified in Section 20
    df_bootstrap = df_pairwise[["metric", "method_1", "method_2", "mean_diff", "ci_lower_95", "ci_upper_95", "cohen_dz", "rank_biserial"]]
    df_bootstrap.to_csv(out_dir / "bootstrap.csv", index=False)

    # 3. Factorial Moderation Regression with HC3
    print("Running HC3 Moderation Regression and Diagnostics...")
    df_moderation, df_diags = run_moderation_analysis(df, metric=args.metric)
    df_moderation.to_csv(out_dir / "moderation.csv", index=False)
    df_diags.to_csv(out_dir / "diagnostics.csv", index=False)

    print(f"All statistical analyses successfully saved to {out_dir}")


if __name__ == "__main__":
    main()
