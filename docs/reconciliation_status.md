# Step 11C-C-2C — Bootstrap and Frozen-Results Reconciliation

## Decision

The frozen manuscript statistical record and the current executable repository outputs are retained as two explicitly identified records. They are not silently merged or substituted.

### Frozen manuscript record

The manuscript was frozen using the audited statistical workbook. The reported primary bootstrap intervals are preserved in:

`results/statistical_analysis/bootstrap_manuscript_frozen.csv`

These intervals use the 5,000-resample bootstrap analysis performed during manuscript development.

### Current executable record

The repository's executable statistical pipeline uses 2,000 bootstrap resamples by default. Its output is:

`results/statistical_analysis/bootstrap.csv`

This table is generated from the current reproduced primary cell-level results.

## Why the records differ

The current executable reproduction was validated as a historical reproduction within the tolerances defined in `config/reproducibility.yaml`; it was not required to reproduce every historical cell-level value byte-for-byte. Consequently, the current paired mean contrasts and bootstrap intervals are not numerically identical to the frozen manuscript-development record. The difference is therefore not attributable solely to the number of bootstrap resamples.

## Scientific interpretation

The estimand is unchanged: a paired confidence interval for method contrasts obtained by resampling experimental cells. The distinction is one of computational record provenance, not a change in the study question or grading methods.

## Release integrity rule

The manuscript remains the authoritative source for the submitted numerical presentation. The frozen bootstrap CSV preserves the exact manuscript-development confidence-interval record, while the executable bootstrap CSV documents what the current release produces. Future regeneration must state which record is being reproduced and must not silently overwrite the other.

## Status

**11C-C-2C: RECONCILED — PASS WITH TRANSPARENT DUAL-RECORD DOCUMENTATION.**

The repository is not yet tagged v1.0.0 because final author metadata, clean-environment validation, manifest regeneration, and checksum regeneration remain release gates.
