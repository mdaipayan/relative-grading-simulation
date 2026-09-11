# Relative Grading Simulation Framework

A research-grade, reproducible simulation framework for:
**“Robust Relative Grading in Engineering Education: Effects of Cohort Size, Score Distributions, Competency Constraints, and Score Perturbations.”**

This software reproduces the frozen Step 7D primary simulation, Step 8B $\rho$-sensitivity analysis, statistical analyses, tables, figures, and validation checks.

---

## 1. Quick Start & Reproduction

### Installation
```bash
cd relative_grading_simulation
pip install -r requirements.txt
pip install -e .
```

### Running Unit Tests
```bash
python -m pytest -o pythonpath=src tests/ -v
```

### End-to-End Reproduction Workflow
To execute the full simulation and analysis pipeline:
```bash
# 1. Execute Primary Factorial Simulation (2,100 cells, R = 1,000)
python scripts/run_primary.py

# 2. Execute Rho Sensitivity Experiment (900 cells, R = 500)
python scripts/run_rho_sensitivity.py

# 3. Execute Statistical Analysis (Friedman, Pairwise Wilcoxon, HC3 Moderation)
python scripts/run_statistics.py

# 4. Generate Publication Figures (Figures 1 through 8)
python scripts/generate_figures.py

# 5. Validate Reproduction against Audited Frozen Baseline
python scripts/validate_reproduction.py
```

For quick bench-testing or development verification:
```bash
# Fast bench test: 10 cells, R = 100
python scripts/run_primary.py --cells-limit 10 --replications 100
```

---

## 2. Directory Structure

```text
relative_grading_simulation/
├── README.md
├── requirements.txt
├── pyproject.toml
├── LICENSE
├── CITATION.cff
│
├── config/
│   ├── primary_design.yaml
│   ├── rho_sensitivity.yaml
│   └── reproducibility.yaml
│
├── src/
│   └── relative_grading/
│       ├── distributions.py
│       ├── assessment.py
│       ├── contamination.py
│       ├── eligibility.py
│       ├── methods/
│       ├── reference.py
│       ├── grading.py
│       ├── metrics.py
│       ├── simulation.py
│       ├── sensitivity.py
│       ├── statistics/
│       ├── results/
│       └── validation/
│
├── scripts/
│   ├── run_primary.py
│   ├── run_rho_sensitivity.py
│   ├── run_statistics.py
│   ├── generate_figures.py
│   └── validate_reproduction.py
│
├── tests/
├── data/
├── results/
├── figures/
└── docs/
```

---

## 3. Five Grading Methods Evaluated

- **M1 — Mean–SD:** Parametric baseline with sample standard deviation ($ddof=1$) and competency overlay $B_7^* = \max(\mu - 1.5s, CE)$.
- **M2 — Percentile:** Calibrated empirical Type-7 quantile operationalization.
- **M3 — Fixed Distribution / Max–Min:** Linear partition of observed score span with competency overlay.
- **M4 — Q-Factor / Constrained:** Study-specific operationalization anchoring lower boundary directly to external competency threshold $CE$.
- **M5 — Median–MAD:** Robust non-parametric comparator using median absolute deviation scaled by $1.4826$.

---

## 4. Scientific Integrity & Audit Policy

The package adheres strictly to the frozen protocol. Deterministic hierarchical random number streams (`master_seed -> cell_seed -> rep_seed`) guarantee exact numerical reproducibility across runs.
