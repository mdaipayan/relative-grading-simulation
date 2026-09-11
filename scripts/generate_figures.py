"""Generate the 8 manuscript figures from stored simulation results."""

import argparse
from pathlib import Path
import sys

# Ensure src is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Method palette and style
COLORS = {
    "MeanSD": "#1f77b4",      # Blue
    "Percentile": "#ff7f0e",  # Orange
    "MaxMin": "#2ca02c",      # Green
    "QFactor": "#d62728",     # Red
    "MedianMAD": "#9467bd",   # Purple
}
MARKERS = {
    "MeanSD": "o",
    "Percentile": "s",
    "MaxMin": "^",
    "QFactor": "D",
    "MedianMAD": "v",
}


def main():
    parser = argparse.ArgumentParser(description="Generate publication figures.")
    parser.add_argument("--primary-results", type=str, default="results/primary/primary_cell_results.parquet")
    parser.add_argument("--rho-results", type=str, default="results/rho_sensitivity/rho_cell_results.parquet")
    parser.add_argument("--output-dir", type=str, default="figures")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load primary results
    prim_path = Path(args.primary_results)
    if not prim_path.exists():
        prim_path = prim_path.with_suffix(".csv")
    if not prim_path.exists():
        print(f"Warning: Primary results not found at {args.primary_results}. Figures 1-6, 8 cannot be rendered yet.")
        df_prim = None
    else:
        df_prim = pd.read_parquet(prim_path) if prim_path.suffix == ".parquet" else pd.read_csv(prim_path)

    # Load rho results
    rho_path = Path(args.rho_results)
    if not rho_path.exists():
        rho_path = rho_path.with_suffix(".csv")
    if not rho_path.exists():
        df_rho = None
    else:
        df_rho = pd.read_parquet(rho_path) if rho_path.suffix == ".parquet" else pd.read_csv(rho_path)

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

    methods = ["MeanSD", "Percentile", "MaxMin", "QFactor", "MedianMAD"]

    if df_prim is not None:
        # Fig 1: Overall Stability
        fig, ax = plt.subplots(figsize=(8, 5))
        ov = df_prim.groupby("method")["mean_grid_stability"].agg(["mean", "std"]).reindex(methods)
        bars = ax.bar(ov.index, ov["mean"], yerr=ov["std"], capsize=5, color=[COLORS[m] for m in methods], alpha=0.85, edgecolor="black")
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 1: Overall Grade Stability Across Five Methods (Primary Design)")
        ax.set_ylim(0.5, 1.0)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.01, f"{h:.4f}", ha="center", va="bottom", fontweight="bold")
        fig.savefig(out_dir / "Fig1_Overall_Stability.png", dpi=300)
        fig.savefig(out_dir / "Fig1_Overall_Stability.pdf")
        plt.close(fig)

        # Fig 2: Cohort Size
        fig, ax = plt.subplots(figsize=(9, 5))
        by_n = df_prim.groupby(["N", "method"])["mean_grid_stability"].mean().unstack(level="method")
        for m in methods:
            if m in by_n.columns:
                ax.plot(by_n.index, by_n[m], marker=MARKERS[m], label=m, color=COLORS[m], linewidth=2)
        ax.set_xlabel("Cohort Size (N)")
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 2: Effect of Cohort Size on Grade Stability")
        ax.set_xticks(by_n.index)
        ax.legend(title="Method")
        fig.savefig(out_dir / "Fig2_Cohort_Size.png", dpi=300)
        fig.savefig(out_dir / "Fig2_Cohort_Size.pdf")
        plt.close(fig)

        # Fig 3: Distribution
        fig, ax = plt.subplots(figsize=(10, 5.5))
        by_dist = df_prim.groupby(["distribution", "method"])["mean_grid_stability"].mean().unstack(level="method")
        x = np.arange(len(by_dist.index))
        width = 0.15
        for i, m in enumerate(methods):
            if m in by_dist.columns:
                ax.bar(x + i*width, by_dist[m], width, label=m, color=COLORS[m], edgecolor="black", alpha=0.85)
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(by_dist.index, rotation=15)
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 3: Grade Stability Across Target Marginal Distributions")
        ax.set_ylim(0.5, 1.0)
        ax.legend(title="Method")
        fig.savefig(out_dir / "Fig3_Distribution.png", dpi=300)
        fig.savefig(out_dir / "Fig3_Distribution.pdf")
        plt.close(fig)

        # Fig 4: CE (Competency Threshold)
        fig, ax = plt.subplots(figsize=(8, 5))
        by_ce = df_prim.groupby(["CE", "method"])["mean_grid_stability"].mean().unstack(level="method")
        for m in methods:
            if m in by_ce.columns:
                ax.plot(by_ce.index, by_ce[m], marker=MARKERS[m], label=m, color=COLORS[m], linewidth=2)
        ax.set_xlabel("Competency Threshold CE (%)")
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 4: Impact of External Competency Threshold on Grade Stability")
        ax.legend(title="Method")
        fig.savefig(out_dir / "Fig4_CE.png", dpi=300)
        fig.savefig(out_dir / "Fig4_CE.pdf")
        plt.close(fig)

        # Fig 5: Contamination level epsilon
        fig, ax = plt.subplots(figsize=(8, 5))
        by_eps = df_prim.groupby(["epsilon", "method"])["mean_grid_stability"].mean().unstack(level="method")
        for m in methods:
            if m in by_eps.columns:
                ax.plot(by_eps.index * 100, by_eps[m], marker=MARKERS[m], label=m, color=COLORS[m], linewidth=2)
        ax.set_xlabel("Contamination Proportion ε (%)")
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 5: Degradation of Grade Stability Under Score Contamination")
        ax.legend(title="Method")
        fig.savefig(out_dir / "Fig5_Contamination.png", dpi=300)
        fig.savefig(out_dir / "Fig5_Contamination.pdf")
        plt.close(fig)

        # Fig 6: Directional Contamination (lower vs upper)
        fig, ax = plt.subplots(figsize=(9, 5))
        by_dir = df_prim[df_prim["epsilon"] > 0].groupby(["direction", "method"])["mean_grid_stability"].mean().unstack(level="method")
        x = np.arange(len(by_dir.index))
        width = 0.15
        for i, m in enumerate(methods):
            if m in by_dir.columns:
                ax.bar(x + i*width, by_dir[m], width, label=m, color=COLORS[m], edgecolor="black", alpha=0.85)
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels([f"{d.capitalize()} Tail" for d in by_dir.index])
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 6: Robustness Under Lower-Tail vs Upper-Tail Contamination")
        ax.set_ylim(0.5, 1.0)
        ax.legend(title="Method")
        fig.savefig(out_dir / "Fig6_Directional_Contamination.png", dpi=300)
        fig.savefig(out_dir / "Fig6_Directional_Contamination.pdf")
        plt.close(fig)

        # Fig 8: Secondary Metrics
        fig, axes = plt.subplots(2, 2, figsize=(11, 8))
        sec_metrics = [
            ("mean_boundary_displacement", "Mean Boundary Displacement", axes[0, 0]),
            ("boundary_rmse", "Boundary RMSE", axes[0, 1]),
            ("pass_rate_sd", "Pass-Rate Variability (SD)", axes[1, 0]),
            ("competency_override_rate", "Competency Override Rate", axes[1, 1]),
        ]
        for col, title, ax_sub in sec_metrics:
            vals = df_prim.groupby("method")[col].mean().reindex(methods)
            ax_sub.bar(vals.index, vals.values, color=[COLORS[m] for m in methods], edgecolor="black", alpha=0.85)
            ax_sub.set_title(title)
            ax_sub.tick_params(axis="x", rotation=25)
        plt.suptitle("Figure 8: Comparative Secondary Performance Metrics", fontsize=13, fontweight="bold")
        fig.savefig(out_dir / "Fig8_Secondary_Metrics.png", dpi=300)
        fig.savefig(out_dir / "Fig8_Secondary_Metrics.pdf")
        plt.close(fig)

    if df_rho is not None:
        # Fig 7: Rho Sensitivity
        fig, ax = plt.subplots(figsize=(8, 5))
        by_rho = df_rho.groupby(["rho", "method"])["mean_grid_stability"].mean().unstack(level="method")
        for m in methods:
            if m in by_rho.columns:
                ax.plot(by_rho.index, by_rho[m], marker=MARKERS[m], label=m, color=COLORS[m], linewidth=2)
        ax.set_xlabel("Assessment Component Correlation (ρ)")
        ax.set_ylabel("Mean Grid Stability")
        ax.set_title("Figure 7: Stability Across Component Correlation Levels (ρ Sensitivity)")
        ax.legend(title="Method")
        fig.savefig(out_dir / "Fig7_Rho_Sensitivity.png", dpi=300)
        fig.savefig(out_dir / "Fig7_Rho_Sensitivity.pdf")
        plt.close(fig)

    print(f"Figures generated and saved to {out_dir}")


if __name__ == "__main__":
    main()
