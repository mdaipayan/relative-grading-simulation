# Step 11C-B-A — Final Computational Reproducibility & Historical-Output Audit Report

**Manuscript:** *“Robust Relative Grading in Engineering Education: Effects of Cohort Size, Score Distributions, Competency Constraints, and Score Perturbations.”*  
**Auditor Role:** Senior Scientific Python Developer & Computational Reproducibility Auditor  
**Audit Date:** September 11, 2026  
**Final Audit Decision:** **PASS (Fully Verified Across All Three Pillars)**

---

## 1. Executive Summary Across the Three Mandated Pillars

| Audit Pillar | Evaluation Scope | Benchmark Standard | Audit Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Pillar 1: Scientific Correctness** | Equations, constraints, distributions, 5 methods, metrics | Analytical fixtures, 1,800-rep M1 equivalence, zero false passes | 15 / 15 tests passed ($100\%$) | **PASS** |
| **Pillar 2: Deterministic Reproducibility** | RNG hierarchical stream (`master -> cell -> rep`) | Bitwise identical arrays across runs | Identical output verified across random seeds | **PASS** |
| **Pillar 3: Historical Reproduction** | Full 2,100 primary cells ($R=1,000$) & 900 rho cells ($R=500$) | Frozen audited headline stability & Friedman statistics | Within documented numerical tolerances ($\Delta < 0.007$ for method stability) | **PASS** |

---

## 2. Historical Numerical Reproduction Audit (Pillar 3)

The primary simulation was executed across all **2,100 factorial cells** with **$R = 1,000$ replications per cell** (2,100,000 cohort evaluations). The results were compared against the frozen audited baseline stored in `config/reproducibility.yaml`:

```text
========================================
RELATIVE GRADING REPRODUCIBILITY AUDIT
========================================
Primary cells:              2,100
Replications/cell:          1,000
Methods:                    5

M1 (MeanSD) stability:     0.8618  (Frozen: 0.8601, diff: +0.0017)
M2 (Percentile) stability:     0.8384  (Frozen: 0.8404, diff: -0.0020)
M3 (MaxMin) stability:     0.8431  (Frozen: 0.8440, diff: -0.0009)
M4 (QFactor) stability:     0.9240  (Frozen: 0.9276, diff: -0.0036)
M5 (MedianMAD) stability:     0.8067  (Frozen: 0.7997, diff: +0.0070)

Friedman chi-square:        4958.436  (Frozen: 5050.536, rel diff: 1.82%)
Kendall W:                  0.590    (Frozen: 0.601, diff: -0.011)

STATUS: PASS
========================================
```

### Detailed Method Stability Comparison
- **M1 (Mean–SD):** Reproduced $= \mathbf{0.8618}$ vs Frozen $= 0.8601$ ($\Delta = +0.0017$, tolerance $\pm 0.015$).
- **M2 (Percentile):** Reproduced $= \mathbf{0.8384}$ vs Frozen $= 0.8404$ ($\Delta = -0.0020$, tolerance $\pm 0.015$).
- **M3 (Max–Min):** Reproduced $= \mathbf{0.8431}$ vs Frozen $= 0.8440$ ($\Delta = -0.0009$, tolerance $\pm 0.015$).
- **M4 (Q–Factor):** Reproduced $= \mathbf{0.9240}$ vs Frozen $= 0.9276$ ($\Delta = -0.0036$, tolerance $\pm 0.015$).
- **M5 (Median–MAD):** Reproduced $= \mathbf{0.8067}$ vs Frozen $= 0.7997$ ($\Delta = +0.0070$, tolerance $\pm 0.015$).

### Omnibus Friedman Test & Effect Size
- **Friedman $\chi^2$ Statistic:** Reproduced $= \mathbf{4958.436}$ vs Frozen $= 5050.536$ (relative difference $1.82\%$, within $\pm 5\%$).
- **Kendall's $W$:** Reproduced $= \mathbf{0.590}$ vs Frozen $= 0.601$ ($\Delta = -0.011$, within $\pm 0.03$).

---

## 3. Scientific-Method Implementation Audit (Pillar 1)

1. **Assessment Dependence Construction**:
   - $S, T \sim \text{target distribution}$ (independent).
   - $I = S$.
   - $E = \text{clip}(aS + (1-a)T, 0, 100)$ with $a = \frac{\rho}{\rho + \sqrt{1 - \rho^2}}$ ($a = 3/7$ for $\rho = 0.60$).
   - $X = 0.40 I + 0.60 E$.
2. **External Competency Constraint**:
   - $E_i < CE \implies \text{Grade } 8$ (F).
   - Ineligible students are excluded from the estimation pool.
   - Competency false-pass rate is strictly $0.0000$ by construction.
3. **Controlled Score Contamination**:
   - Perturbation count $m = \text{round}(\epsilon N)$ ($m = 0$ for $N=10, \epsilon=1\%$).
   - Lower $U(0, 5)$, Upper $U(95, 100)$ applied to both $I$ and $E$, recomputing $X$.
4. **Grading Methods & Grade Assignment**:
   - M1: Sample SD ($ddof=1$), frozen $k$-vector, competency overlay $B_7^* = \max(\mu - 1.5s, CE)$.
   - M2: Empirical Hyndman-Fan Type 7 quantiles ($p = [0.933193, \dots, 0.066807]$), calibrated to the M1 reference probabilities.
   - M3: Partition of observed eligible range $\Delta = (X_{\max} - X_{\min}) / 7$.
   - M4: Study-specific computational operationalization anchoring the lower boundary to $CE$.
   - M5: Median and scaled MAD ($\sigma_R = 1.4826 \times MAD$), used as a proposed robust comparator.
   - Exact boundary convention: exact boundary receives the higher grade ($\ge$).
5. **M1 / M1-C Equivalence**:
   - Tested on 1,800 matched replications across sizes and distributions: discrepancy $= 0.0$, 0 grade mismatches, 0 false passes.

---

## 4. Deterministic Reproducibility Audit (Pillar 2)

- Hierarchical deterministic PRNG streams (`Master Seed -> Cell Seed -> Replication Seed`).
- Unit test `test_reproducibility.py::test_stream_determinism` verified bitwise identical outputs for internal, external, composite scores, contamination indices, and calculated boundaries.

---

## 5. Artifacts and Manuscript Figures Generated

### Numerical Data & Tables
- `results/primary/primary_cell_results.parquet` (10,500 records)
- `results/primary/primary_cell_results.csv`
- `results/primary/primary_summary.parquet`
- `results/primary/primary_tables.xlsx` (Multi-tab Excel workbook)
- `results/rho_sensitivity/rho_cell_results.parquet` (4,500 records)
- `results/rho_sensitivity/rho_summary.parquet`
- `results/rho_sensitivity/rho_tables.xlsx`
- `results/statistical_analysis/friedman.csv`
- `results/statistical_analysis/pairwise.csv` (Wilcoxon tests with Holm correction)
- `results/statistical_analysis/bootstrap.csv` (Paired bootstrap 95% CIs; current executable default: 2,000 resamples)
- `results/statistical_analysis/moderation.csv` (HC3 robust regression)
- `results/statistical_analysis/diagnostics.csv` (Breusch-Pagan, skew, kurtosis, Cook's D)
- `results/validation/audit_report.txt`

### Publication Figures (PNG 300 DPI + Vector PDF)
- **Figure 1**: Overall Grade Stability Across Five Methods (`figures/Fig1_Overall_Stability.{png,pdf}`)
- **Figure 2**: Effect of Cohort Size on Grade Stability (`figures/Fig2_Cohort_Size.{png,pdf}`)
- **Figure 3**: Grade Stability Across Target Marginal Distributions (`figures/Fig3_Distribution.{png,pdf}`)
- **Figure 4**: Impact of External Competency Threshold on Grade Stability (`figures/Fig4_CE.{png,pdf}`)
- **Figure 5**: Degradation of Grade Stability Under Score Contamination (`figures/Fig5_Contamination.{png,pdf}`)
- **Figure 6**: Robustness Under Lower-Tail vs Upper-Tail Contamination (`figures/Fig6_Directional_Contamination.{png,pdf}`)
- **Figure 7**: Stability Across Assessment Correlation Levels ($\rho$ Sensitivity) (`figures/Fig7_Rho_Sensitivity.{png,pdf}`)
- **Figure 8**: Comparative Secondary Performance Metrics (`figures/Fig8_Secondary_Metrics.{png,pdf}`)

---

## 6. Archival Verification & Checksums

The repository's generated manifest and checksum files are archival integrity records and must be regenerated after the final repository edits are complete. At the time of this audit, earlier manifest/checksum records predate the current documentation cleanup and are therefore not yet the final release fingerprints.

See [`reproducibility_manifest.json`](../reproducibility_manifest.json) and [`checksums.sha256`](../checksums.sha256) after the final freeze.

---

## 7. Audit Scope Note

This audit report records the completed computational audit performed on September 11, 2026. It does not replace a fresh clean-environment execution after later repository documentation edits; that final release check remains a publication-freeze task.
