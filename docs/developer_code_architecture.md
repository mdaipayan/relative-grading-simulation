# Developer Specification — Relative Grading Reproducibility Simulation

## 1. Purpose

Build a research-grade, reproducible Python simulation framework for the paper:

**“Robust Relative Grading in Engineering Education: Effects of Cohort Size, Score Distributions, Competency Constraints, and Score Perturbations.”**

The software must reproduce the frozen Step 7D primary simulation, Step 8B rho-sensitivity analysis, statistical analyses, tables, figures, and validation checks.

**Critical rule:** Do not invent, alter, or silently reinterpret the frozen scientific protocol. If an implementation detail is genuinely unspecified, flag it explicitly for review instead of guessing.

---

## 2. Scientific Freeze

The following are frozen and must not be changed without reopening the relevant research stage:

### Primary design

- Primary experimental cells: **2,100**
- Replications per cell: **R = 1,000**
- Methods: **5**
- Reference cohort: **Nref = 100,000**
- Cohort sizes:
  `10, 15, 20, 25, 30, 40, 50, 75, 100, 200`
- Distributions: **6**
  - Normal
  - Compressed Normal
  - Uniform
  - Right-skewed Beta(2,5)
  - Left-skewed Beta(5,2)
  - Bimodal 50/50 Beta(2,5)/Beta(5,2)
- Competency thresholds:
  `CE = 10%, 15%, 20%, 25%, 30% of the external component`
- Contamination:
  `epsilon = 0%, 1%, 5%, 10%`
- Nonzero contamination directions:
  - lower-tail: U(0,5)
  - upper-tail: U(95,100)
- Contamination amount:
  `m = round(epsilon * N)`
- For N=10 and epsilon=1%, m=0; record actual m.
- Assessment:
  `X = 0.40 I + 0.60 E`
- Primary dependence construction:
  `E = a*S + (1-a)*T`, with `a = 3/7`
- S and T are independent draws from the same target marginal distribution.
- Scores are clipped to [0,100] where specified by the frozen protocol.
- External competency:
  `E_i < CE => F`
- Students failing external competency are excluded from the relative-grading estimation pool.
- Reference score grid:
  `x = 0,1,...,100`
- Exact boundary receives the higher grade.
- Empirical quantile convention:
  **Hyndman–Fan Type 7 / linear interpolation**
- Standard deviation:
  **sample SD, ddof=1**

---

## 3. Five Frozen Methods

### M1 — Mean–SD

For eligible estimation scores:

`B_j = mu + k_j*s`

where:

`k = [1.5, 1.0, 0.5, 0, -0.5, -1.0, -1.5]`

Final P/F:

`B7* = max(mu - 1.5*s, CE)`

---

### M2 — Percentile

Frozen percentile vector:

`p = [0.933193, 0.841345, 0.691462, 0.500000, 0.308538, 0.158655, 0.066807]`

Use empirical Type-7 quantiles.

**Important:** This is a **study-specific operationalization calibrated to M1**, not a universal educational grading rule.

---

### M3 — Fixed Distribution / Max–Min

For eligible scores:

`Delta = (Xmax - Xmin) / 7`

`Bj = Xmax - j*Delta`, j=1,...,6

`B7 = Xmin`

Then apply competency overlay:

`B7* = max(Xmin, CE)`

Use observed eligible-score extrema.

---

### M4 — Q-Factor / Constrained

This is a **study-specific computational operationalization** of the published Q-factor framework.

Set:

`Qa = CE`

`Sa = Xmax`

For j=1,...,6:

`Bj = Qa + ((7-j)/7)*(Sa-Qa)`

and:

`B7 = Qa`

Do not describe these exact equations as if they were directly published equations unless the source explicitly supports that claim.

---

### M5 — Median–MAD

For eligible scores:

`M = median(X)`

`MAD = median(abs(X-M))`

`sigma_R = 1.4826 * MAD`

Then:

`Bj = M + k_j*sigma_R`

using the same M1 k-vector.

Final P/F:

`B7* = max(M - 1.5*sigma_R, CE)`

**Important:** M5 is a **proposed robust comparator**, not an established educational grading algorithm.

---

## 4. Core Architecture

Use modular Python architecture:

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
│       ├── __init__.py
│       ├── distributions.py
│       ├── assessment.py
│       ├── contamination.py
│       ├── eligibility.py
│       │
│       ├── methods/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── mean_sd.py
│       │   ├── percentile.py
│       │   ├── max_min.py
│       │   ├── q_factor.py
│       │   └── median_mad.py
│       │
│       ├── reference.py
│       ├── grading.py
│       ├── metrics.py
│       ├── simulation.py
│       ├── sensitivity.py
│       │
│       ├── statistics/
│       │   ├── friedman.py
│       │   ├── pairwise.py
│       │   ├── bootstrap.py
│       │   ├── moderation.py
│       │   └── diagnostics.py
│       │
│       ├── results/
│       │   ├── collector.py
│       │   ├── summaries.py
│       │   └── export.py
│       │
│       └── validation/
│           ├── equations.py
│           ├── equivalence.py
│           └── frozen_values.py
│
├── scripts/
│   ├── run_primary.py
│   ├── run_rho_sensitivity.py
│   ├── run_statistics.py
│   ├── generate_figures.py
│   └── validate_reproduction.py
│
├── tests/
│   ├── test_distributions.py
│   ├── test_methods.py
│   ├── test_competency.py
│   ├── test_contamination.py
│   ├── test_metrics.py
│   ├── test_m1_equivalence.py
│   └── test_reproducibility.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── reference/
│
├── results/
│   ├── primary/
│   ├── rho_sensitivity/
│   └── statistical_analysis/
│
├── figures/
│
└── docs/
    ├── protocol.md
    ├── mathematical_specification.md
    └── results_mapping.md
```

---

## 5. Design Principles

1. **Do not build one giant script.**
2. Separate:
   - data generation
   - assessment construction
   - eligibility
   - contamination
   - grading methods
   - reference construction
   - grade assignment
   - metrics
   - simulation
   - statistical analysis
   - validation
3. Every scientific parameter must come from configuration.
4. Random-number generation must use explicit deterministic seed streams.
5. Results must be written first to machine-readable formats such as CSV/Parquet; Excel is a reporting/export layer.
6. Do not round intermediate calculations.
7. Record actual contamination count `m`.
8. Record infeasible cases rather than silently dropping them.
9. Preserve enough metadata to reproduce every experimental cell.
10. Keep publication tables/figures separate from the core computational engine.

---

## 6. Distribution Module

Implement:

```python
generate_scores(distribution, n, rng) -> np.ndarray
```

Required distributions:

### Normal

`clip(60 + 15*Z, 0, 100)`

### Compressed

`clip(60 + 5*Z, 0, 100)`

### Uniform

`U(0,100)`

### Right-skewed

`100 * Beta(2,5)`

### Left-skewed

`100 * Beta(5,2)`

### Bimodal

50/50 mixture of:

`100*Beta(2,5)`

and

`100*Beta(5,2)`

---

## 7. Assessment Module

Implement the frozen construction:

```python
generate_assessment(n, distribution, rho, rng)
```

Primary model:

```text
S ~ target distribution
T ~ target distribution
S independent of T

I = S

E = a*S + (1-a)*T
a = 3/7

E = clip(E, 0, 100) where required

X = 0.40*I + 0.60*E
```

The implementation must retain:

- I
- E
- X

Do not return only aggregate X.

The primary construction gives approximately rho=0.60 pre-clipping for equal-variance components; do not represent this as an empirical institutional correlation.

---

## 8. Eligibility Module

Implement:

```python
get_eligible_pool(internal, external, total, CE)
```

Return:

- eligibility mask
- eligible scores
- eligible N
- ineligible N
- eligibility rate

Rule:

`E < CE => F`

Only eligible students enter the relative-grading estimation pool.

---

## 9. Contamination Module

Implement:

```python
contaminate(internal, external, epsilon, direction, rng)
```

Rules:

```text
lower -> U(0,5)
upper -> U(95,100)
```

Number contaminated:

`m = round(epsilon*N)`

Select the specified number of positions and apply the perturbation to both I and E, then recompute X.

Record:

- epsilon
- direction
- requested m
- actual m
- affected indices if needed for audit

Terminology in documentation must be:

**controlled score contamination / outlier perturbation**

not cheating, malpractice, or misconduct.

---

## 10. Grading Method Interface

Create a common abstract interface:

```python
class GradingMethod(ABC):
    name: str

    @abstractmethod
    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float
    ) -> np.ndarray:
        ...
```

Methods:

```text
MeanSD
Percentile
MaxMin
QFactor
MedianMAD
```

The simulation engine should not contain method-specific mathematical logic.

---

## 11. Grade Assignment

Create exactly one authoritative function:

```python
assign_grade(score, boundaries)
```

Rule:

**Exact boundary receives the higher grade.**

Do not duplicate grade-assignment logic in individual methods.

---

## 12. Reference Cohort

Implement a reference-cohort builder using:

`Nref = 100000`

For every relevant experimental condition, calculate the reference method boundaries and reference grade assignment.

Reference score grid:

`0,1,2,...,100`

Do not use the reference cohort to replace the finite-cohort simulation.

---

## 13. Primary Metrics

Implement the following.

### Primary stability

For each reference score x:

`p_g(x) = proportion of replications assigning grade g`

`stability(x) = max_g p_g(x)`

Aggregate:

`mean_grid_stability = mean(stability(x))` over x=0,...,100

### Reference disagreement

Proportion of replications where the grade for x differs from the clean-reference grade.

### Boundary displacement

Mean absolute boundary displacement:

`mean(abs(B_rep - B_reference))`

### Boundary RMSE

`sqrt(mean((B_rep - B_reference)^2))`

---

## 14. Secondary Metrics

Implement:

### Pass-rate variability

SD of proportion passing across valid replications.

### Grade-count variability

SD of grade proportions across valid replications.

### Outlier sensitivity

Boundary-vector difference between matched clean and contaminated scenarios.

### Competency override rate

Proportion of students satisfying the method-native passing condition but failing external competency.

Final false-pass rate after the competency rule should be zero by construction.

### Feasibility

Flag cases where the eligible estimation pool is below the minimum required by the computational grading procedure.

Never silently discard such cases.

---

## 15. Primary Simulation

Primary cell structure:

```text
N × Distribution × CE × Contamination × Direction
```

There are:

```text
10 × 6 × 5 × 7 = 2,100 cells
```

with:

```text
R = 1,000
```

replications per cell.

The implementation must preserve cell identifiers:

```text
cell_id
N
distribution
CE
epsilon
direction
replication
method
```

---

## 16. Rho Sensitivity Experiment

This is a **focused sensitivity analysis**, not another full factorial experiment.

Frozen design:

- rho = `0, 0.3, 0.6, 0.8, 0.9`
- CE = `20%`
- conditions:
  - clean
  - 5% lower contamination
  - 5% upper contamination
- 10 cohort sizes
- 6 distributions
- 3 contamination conditions
- 180 cells per rho
- 900 cells total
- R = 500 per cell
- 450,000 cohort replications total

Do not describe this as a second full factorial.

---

## 17. Statistical Analysis

Separate simulation from analysis.

Implement:

### Omnibus

Friedman test across five methods, paired by experimental cell.

Report:

- chi-square
- p-value
- Kendall's W

Expected primary audit:

`chi-square = 5050.535584`

`Kendall W = 0.6013`

### Pairwise

Wilcoxon signed-rank tests across 2,100 cells.

Apply Holm correction within each metric.

Report:

- raw p
- Holm-adjusted p
- mean paired difference
- paired bootstrap 95% CI
- Cohen dz
- rank-biserial correlation

### Moderation

For M4 minus each comparator:

```text
diff ~ C(N)
     + C(Distribution)
     + C(CE)
     + C(Contamination)
     + C(N):C(Contamination)
     + C(Distribution):C(Contamination)
     + C(CE):C(Contamination)
```

Use HC3 robust covariance.

Do not describe interaction results as universal effects; describe them as evidence **within the specified factorial model**.

### Diagnostics

Include:

- R²
- adjusted R²
- Breusch–Pagan
- residual skew
- excess kurtosis
- Cook's distance

Use HC3 because heteroscedasticity is expected/observed.

---

## 18. Validation

Create automated tests for:

### M1/M1-C equivalence

M1-C is NOT a sixth method.

Expected:

- 1,800/1,800 matched pilot replications identical
- maximum absolute boundary difference = 0
- 0 grade mismatches
- competency false-pass rate = 0

### Frozen headline values

Validation should compare reproduced aggregate values against frozen audited values within explicitly documented numerical tolerances.

Primary stability expected:

```text
M1 0.8601
M2 0.8404
M3 0.8440
M4 0.9276
M5 0.7997
```

Other frozen values should be stored in a validation configuration, not hard-coded throughout the simulation engine.

---

## 19. Reproducibility

Use deterministic RNG streams.

Preferred pattern:

```python
master_seed
    |
    +-- cell seed
           |
           +-- replication seed
```

Do not rely on uncontrolled global random state.

Record:

- Python version
- package versions
- OS/platform if relevant
- master seed
- configuration hash
- code commit hash if Git is available
- execution timestamp
- cell identifiers

---

## 20. Output Architecture

Recommended files:

```text
results/
├── primary/
│   ├── primary_cell_results.parquet
│   ├── primary_summary.parquet
│   └── primary_metadata.json
│
├── rho_sensitivity/
│   ├── rho_cell_results.parquet
│   └── rho_summary.parquet
│
└── statistical_analysis/
    ├── friedman.csv
    ├── pairwise.csv
    ├── bootstrap.csv
    ├── moderation.csv
    └── diagnostics.csv
```

Excel workbooks should be generated from these results rather than serving as the computational source of truth.

---

## 21. Figure Generation

Generate the eight manuscript figures programmatically:

```text
Fig1_Overall_Stability
Fig2_Cohort_Size
Fig3_Distribution
Fig4_CE
Fig5_Contamination
Fig6_Directional_Contamination
Fig7_Rho_Sensitivity
Fig8_Secondary_Metrics
```

Figures must be reproducible from stored result files.

---

## 22. Development Sequence

Do NOT launch the full simulation first.

### Phase 1 — Core mathematics

1. distributions
2. assessment
3. eligibility
4. contamination

### Phase 2 — Methods

5. base interface
6. M1
7. M2
8. M3
9. M4
10. M5

### Phase 3 — Validation

11. grade assignment
12. M1/M1-C equivalence
13. boundary tests
14. competency tests

### Phase 4 — Reference and metrics

15. reference
16. metrics

### Phase 5 — Simulation

17. primary simulation
18. rho sensitivity

### Phase 6 — Statistics

19. Friedman
20. pairwise
21. bootstrap
22. HC3 moderation
23. diagnostics

### Phase 7 — Publication reproduction

24. tables
25. figures
26. Excel export
27. validation report

---

## 23. Mandatory Development Test

Before the full experiment, run:

```text
N = 10
one distribution
CE = 20%
clean
R = 5
```

Verify manually and through tests:

```text
scores
  ↓
eligibility
  ↓
M1 M2 M3 M4 M5
  ↓
boundaries
  ↓
grade assignment
  ↓
metrics
```

Then progressively test:

```text
R = 5
R = 100
R = 1000
```

Only launch the full 2,100 × 1,000 experiment after the validation suite passes.

---

## 24. Reproduction Commands

Final intended CLI:

```bash
python scripts/run_primary.py
python scripts/run_rho_sensitivity.py
python scripts/run_statistics.py
python scripts/generate_figures.py
python scripts/validate_reproduction.py
```

The final validation command should produce a concise audit such as:

```text
========================================
RELATIVE GRADING REPRODUCIBILITY AUDIT
========================================

Primary cells:              2,100
Replications/cell:          1,000
Methods:                    5

M1 stability:               0.8601
M2 stability:               0.8404
M3 stability:               0.8440
M4 stability:               0.9276
M5 stability:               0.7997

Friedman chi-square:        5050.536
Kendall W:                  0.601

STATUS: PASS
========================================
```

---

## 25. Publication Integrity Rules

The developer must NEVER:

- modify simulation parameters to improve a result;
- delete unfavorable replications;
- silently remove infeasible cells;
- alter frozen equations;
- change a method definition without recording it;
- replace missing source code with an invented claim that it is the original code;
- describe M5 as an established educational grading method;
- describe M4 equations as directly published if they are the study-specific operationalization;
- describe contamination as cheating;
- describe rho values as empirical institutional correlations;
- claim universal superiority of M4.

If a discrepancy is discovered between reproduced results and the frozen manuscript:

1. stop the reproduction claim;
2. identify the discrepancy;
3. report which artifact differs;
4. do not force the code to match the manuscript;
5. determine whether the issue is implementation, archived-result, or manuscript error;
6. reopen the appropriate research stage if a scientific change is required.

---

## 26. Deliverables

The final developer deliverable should contain:

```text
1. Executable source code
2. Configuration files
3. Unit tests
4. Primary simulation outputs
5. Rho sensitivity outputs
6. Statistical-analysis outputs
7. Reproduced figures
8. Reproduced tables
9. Validation report
10. Environment specification
11. README
12. CITATION.cff
13. LICENSE
14. Reproducibility manifest
15. SHA-256 checksums
```

The package must be suitable for archival deposition in a repository such as Zenodo.

---

## 27. Definition of Done

The implementation is complete only when:

- all unit tests pass;
- the primary experiment runs from configuration;
- the rho sensitivity runs independently;
- all five methods are independently testable;
- M1/M1-C equivalence passes;
- the reference cohort is reproducible;
- all primary metrics reproduce;
- statistical analysis reproduces;
- figures regenerate;
- tables regenerate;
- headline values agree with frozen audit values within documented tolerance;
- every output can be traced to a configuration and code version;
- README instructions allow another researcher to reproduce the analysis.

**Build for auditability first, speed second.**
