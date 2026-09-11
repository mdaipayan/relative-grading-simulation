# Bootstrap Reconciliation Note

## Purpose

This note records the relationship between the executable repository implementation and the bootstrap analyses used during manuscript development. It is included to prevent an apparent discrepancy in bootstrap-resample counts from being silently interpreted as a scientific-method change.

## Current executable implementation

The repository's `paired_bootstrap_ci` implementation uses **2,000 resamples by default**. The command-line statistical analysis script likewise defaults to 2,000 and permits the value to be changed with `--n-boot`.

This is the reproducibility setting for the current software release.

## Historical manuscript-development analyses

Earlier manuscript-audit stages used larger bootstrap counts (including 5,000-resample checks) during development and numerical auditing. Those analyses were part of manuscript validation rather than a change to the scientific estimand. The bootstrap estimand remains the paired confidence interval for method contrasts obtained by resampling experimental cells.

The repository therefore does **not** claim that every historical bootstrap confidence interval was generated with the current 2,000-resample default. The release documentation instead makes the current executable setting explicit.

## Release rule

Before final publication release, the manuscript's reported bootstrap intervals and the repository's stored `bootstrap.csv` must be checked together. If the submitted manuscript reports intervals generated with a different resample count, the manuscript methods and supplementary reproducibility note should state that count explicitly. If the manuscript is regenerated from the release code, the reported intervals should be regenerated with the release setting and the manuscript values updated accordingly.

No other statistical method, estimand, or simulation factor is changed by this reconciliation note.
