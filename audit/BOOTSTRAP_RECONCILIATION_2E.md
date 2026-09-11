# Bootstrap Reconciliation — Release Audit

## Current executable record

- `paired_bootstrap_ci`: 2,000 resamples by default.
- `scripts/run_statistics.py`: `--n-boot 2000` by default.
- Current output: `results/statistical_analysis/bootstrap.csv`.

## Frozen manuscript record

- Preserved as: `results/statistical_analysis/bootstrap_manuscript_frozen.csv`.
- Bootstrap-resample count recorded there: 5,000.
- Contains the ten paired method contrasts underlying the frozen manuscript statistical record.

## Release interpretation

These records are retained separately. The current executable output is the reproducible software record; the frozen file is the historical provenance record for the manuscript-development confidence intervals.

A difference in bootstrap-resample count does not by itself change the estimand: both procedures estimate paired confidence intervals for method contrasts by resampling experimental cells.

## Release blocker

Before `v1.0.0` is tagged, the submitted manuscript must explicitly identify the bootstrap configuration used for its reported confidence intervals. Do not overwrite the frozen manuscript record or force fresh bootstrap output to match it without a documented scientific reason.
