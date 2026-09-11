# Results and Artifacts Mapping

This document maps manuscript tables, figures, and statistical analyses to their corresponding computational source artifacts.

| Manuscript Item | Description | Computational Output File | Generating Script |
| :--- | :--- | :--- | :--- |
| **Figure 1** | Overall Grade Stability (5 methods) | `figures/Fig1_Overall_Stability.png` | `scripts/generate_figures.py` |
| **Figure 2** | Cohort Size Effect ($N=10 \dots 200$) | `figures/Fig2_Cohort_Size.png` | `scripts/generate_figures.py` |
| **Figure 3** | Distributional Sensitivity (6 dists) | `figures/Fig3_Distribution.png` | `scripts/generate_figures.py` |
| **Figure 4** | Competency Threshold Effect ($CE=10..30\%$) | `figures/Fig4_CE.png` | `scripts/generate_figures.py` |
| **Figure 5** | Score Contamination ($\epsilon=0..10\%$) | `figures/Fig5_Contamination.png` | `scripts/generate_figures.py` |
| **Figure 6** | Directional Perturbation (Lower vs Upper) | `figures/Fig6_Directional_Contamination.png` | `scripts/generate_figures.py` |
| **Figure 7** | Assessment Correlation Sensitivity ($\rho$) | `figures/Fig7_Rho_Sensitivity.png` | `scripts/generate_figures.py` |
| **Figure 8** | Secondary Performance Metrics | `figures/Fig8_Secondary_Metrics.png` | `scripts/generate_figures.py` |
| **Table 1** | Primary Design Overall Summary | `results/primary/primary_summary.parquet` | `scripts/run_primary.py` |
| **Table 2** | Factorial Workbook (Excel) | `results/primary/primary_tables.xlsx` | `scripts/run_primary.py` |
| **Table 3** | Omnibus Friedman Test | `results/statistical_analysis/friedman.csv` | `scripts/run_statistics.py` |
| **Table 4** | Pairwise Wilcoxon Comparisons | `results/statistical_analysis/pairwise.csv` | `scripts/run_statistics.py` |
| **Table 5** | Paired Bootstrap 95% CIs | `results/statistical_analysis/bootstrap.csv` | `scripts/run_statistics.py` |
| **Table 6** | HC3 Moderation Regression | `results/statistical_analysis/moderation.csv` | `scripts/run_statistics.py` |
| **Table 7** | Regression Diagnostics | `results/statistical_analysis/diagnostics.csv` | `scripts/run_statistics.py` |
| **Audit** | Reproducibility Audit Report | `results/validation/audit_report.txt` | `scripts/validate_reproduction.py` |
