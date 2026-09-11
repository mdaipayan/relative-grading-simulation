# Relative Grading Simulation Framework

Reproducible computational framework supporting the study:

> **Robust Relative Grading in Engineering Education: Effects of Cohort Size, Score Distributions, Competency Constraints, and Score Perturbations**

This repository contains the executable simulation framework, frozen experimental configurations, statistical-analysis code, validation tests, generated results, publication figures, and documentation supporting the study.

## Reproducibility status

Two distinct properties are reported:

- **Deterministic reproducibility:** the same software configuration and seed hierarchy produce identical outputs under the supported environment.
- **Historical numerical reproduction:** the current implementation is compared with archived frozen study baselines and accepted when differences fall within the tolerances defined in `config/reproducibility.yaml`.

The completed computational audit reports PASS for scientific-method implementation, deterministic reproducibility, and historical numerical reproduction. The detailed audit trail is retained in `docs/` and `results/validation/`.

## Study design

### Primary experiment

```text
10 cohort sizes
× 6 score distributions
× 5 competency thresholds
× 7 contamination conditions
= 2,100 experimental cells

1,000 replications per cell
Reference cohort = 100,000
Reference grid = 0–100 in unit increments
```

Cohort sizes:

```text
10, 15, 20, 25, 30, 40, 50, 75, 100, 200
```

Distributions:

```text
Normal
Compressed Normal
Uniform
Right-skewed
Left-skewed
Bimodal
```

Competency thresholds:

```text
10, 15, 20, 25, 30 percent of the external component
```

Contamination conditions:

```text
0%, 1%, 5%, 10%
```

For nonzero contamination, lower perturbations are sampled from `U(0,5)` and upper perturbations from `U(95,100)`. The number of perturbed observations is `round(epsilon*N)`.

### Focused dependence sensitivity

```text
5 dependence values
× 10 cohort sizes
× 6 distributions
× 3 contamination conditions
× 1 competency threshold
= 900 cells

500 replications per cell
CE = 20
Reference cohort = 100,000
```

The sensitivity parameter is a **target pre-clipping dependence parameter** in the score-generation model. It should not automatically be interpreted as the realized post-clipping sample correlation.

The assessment construction is:

```text
I = S
E = a*S + (1-a)*T
X = 0.40*I + 0.60*E
```

where `S` and `T` are independent draws from the same target marginal distribution. The implementation maps the sensitivity parameter to `a` using the analytical equal-variance pre-clipping relationship documented in `src/relative_grading/assessment.py`.

## Grading methods

Five methods are evaluated:

1. **M1 — Mean–SD:** parametric baseline using sample standard deviation (`ddof=1`) with a competency-constrained lower boundary.
2. **M2 — Percentile:** study-specific empirical Type-7 quantile operationalization calibrated to the M1 reference probabilities.
3. **M3 — Fixed Distribution / Max–Min:** linear partition of the observed score span with competency constraint.
4. **M4 — Q-Factor / Constrained:** study-specific computational operationalization anchoring the lower boundary to the external competency threshold.
5. **M5 — Median–MAD:** proposed robust comparator using the median absolute deviation scaled by `1.4826`.

M4 is **not** claimed to be universally superior. M5 is **not** presented as an established educational grading standard.

## Installation

The audited environment used Python 3.12.0.

```bash
pip install -r requirements.txt
pip install -e .
```

For development/testing:

```bash
pip install -e ".[dev]"
```

## Tests

Run the complete test suite:

```bash
python -m pytest -o pythonpath=src tests/ -v
```

The audited baseline contains 15 passing tests.

## End-to-end reproduction

Run in this order:

```bash
# 1. Primary factorial simulation
python scripts/run_primary.py

# 2. Dependence sensitivity analysis
python scripts/run_rho_sensitivity.py

# 3. Statistical analysis
python scripts/run_statistics.py

# 4. Publication figures
python scripts/generate_figures.py

# 5. Historical-baseline validation
python scripts/validate_reproduction.py
```

For a quick development check:

```bash
python scripts/run_primary.py --cells-limit 10 --replications 100
```

## Repository structure

```text
relative-grading-simulation/
├── README.md
├── requirements.txt
├── pyproject.toml
├── LICENSE
├── CITATION.cff
├── reproducibility_manifest.json
├── checksums.sha256
│
├── config/
│   ├── primary_design.yaml
│   ├── rho_sensitivity.yaml
│   └── reproducibility.yaml
│
├── src/relative_grading/
│   ├── distributions.py
│   ├── assessment.py
│   ├── contamination.py
│   ├── eligibility.py
│   ├── grading.py
│   ├── metrics.py
│   ├── simulation.py
│   ├── sensitivity.py
│   ├── methods/
│   ├── statistics/
│   ├── results/
│   └── validation/
│
├── scripts/
│   ├── run_primary.py
│   ├── run_rho_sensitivity.py
│   ├── run_statistics.py
│   ├── generate_figures.py
│   ├── generate_manifest.py
│   └── validate_reproduction.py
│
├── tests/
├── results/
├── figures/
└── docs/
```

## Validation and audit

The validation configuration stores the frozen headline values and explicit tolerances in `config/reproducibility.yaml`.

Frozen primary mean grid stability:

| Method | Stability |
|---|---:|
| M1 — Mean–SD | 0.8601 |
| M2 — Percentile | 0.8404 |
| M3 — Max–Min | 0.8440 |
| M4 — Q-Factor | 0.9276 |
| M5 — Median–MAD | 0.7997 |

Frozen statistical baselines:

```text
Friedman chi-square = 5050.535584
Kendall's W         = 0.6013
```

The validation script reads tolerances from `config/reproducibility.yaml`; tolerances are not duplicated in the README.

## Data and generated outputs

Generated cell-level and summary outputs, statistical outputs, and publication figures are retained in the repository to support auditability of the reported analyses.

## Citation

If you use this software or its generated results, please cite the associated study and the software release identified in `CITATION.cff`.

The `CITATION.cff` metadata should be updated with the archival DOI when the publication release is deposited in Zenodo or another persistent repository.

## License

The software is released under the MIT License. See `LICENSE`.

## Research integrity note

The simulation uses synthetic score distributions and controlled score perturbations. The contamination factor represents a simulation condition for assessing robustness to unusual observations; it is not a model of academic misconduct.

The dependence parameter is a computational parameter and is not an empirical estimate of institutional assessment correlation.
