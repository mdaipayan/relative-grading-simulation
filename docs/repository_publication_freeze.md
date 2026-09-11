# Repository Publication Freeze

## Purpose

This document defines the final checks required before tagging a publication release of the relative-grading simulation repository.

## Scientific freeze

- [x] Primary design is stored in `config/primary_design.yaml`.
- [x] Rho sensitivity design is stored in `config/rho_sensitivity.yaml`.
- [x] Frozen numerical baselines and tolerances are stored in `config/reproducibility.yaml`.
- [x] Five grading methods are implemented in the `src/relative_grading/methods/` package.
- [x] Competency enforcement and exact-boundary grading are covered by tests.
- [x] M1/M1-C equivalence is covered by tests.

## Reproducibility freeze

- [x] Deterministic hierarchical random streams are implemented.
- [x] Primary experiment: 2,100 cells, 1,000 replications per cell, reference cohort 100,000.
- [x] Rho sensitivity: 900 cells, 500 replications per cell, CE = 20, reference cohort 100,000.
- [x] Historical validation uses tolerances defined in `config/reproducibility.yaml`.
- [ ] Final clean-environment reproduction executed immediately before release tag.

## Documentation freeze

- [x] README distinguishes deterministic reproducibility from historical numerical reproduction.
- [x] README describes the dependence parameter as a simulation/pre-clipping parameter rather than an empirical institutional estimate.
- [x] M5 is identified as a proposed robust comparator.
- [x] M4 is described as a study-specific computational operationalization.
- [x] M2 is described as a study-specific calibrated empirical operationalization.
- [x] Bootstrap-resampling provenance has been reconciled and documented; the frozen manuscript statistical record is preserved separately from current executable output.

## Metadata freeze

- [x] Repository URL is correct in `CITATION.cff`.
- [x] Final software author is identified as Daipayan Mandal in `CITATION.cff`.
- [x] Package author metadata is synchronized in `pyproject.toml`.
- [ ] Archival DOI must be added to `CITATION.cff` after DOI creation.
- [ ] `reproducibility_manifest.json` must be regenerated after all final file changes.
- [ ] `checksums.sha256` must be regenerated after all final file changes.

## Release rule

Do not create the final publication tag until all unchecked release-blocking items above are resolved. The repository version associated with the manuscript should be immutable after archival deposition except for documented post-publication corrections.
