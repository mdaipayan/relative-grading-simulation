"""Executable script for running the frozen primary simulation experiment."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import os
from pathlib import Path
import platform
import sys
import time
from typing import List, Dict, Any, Tuple

# Ensure src is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from relative_grading.simulation import (
    CellSpec,
    build_primary_cell_grid,
    run_cell_simulation,
)
from relative_grading.reference import ReferenceCohortManager
from relative_grading.results.summaries import aggregate_primary_summaries
from relative_grading.results.export import export_results_to_excel


def _worker_task(args: Tuple) -> List[Dict[str, Any]]:
    cell, reps, master_seed, ref_cache = args
    return run_cell_simulation(cell, reps, master_seed, ref_cache)


def main():
    parser = argparse.ArgumentParser(description="Execute primary relative grading simulation.")
    parser.add_argument("--config", type=str, default="config/primary_design.yaml", help="Path to primary design config")
    parser.add_argument("--repro-config", type=str, default="config/reproducibility.yaml", help="Path to reproducibility config")
    parser.add_argument("--replications", type=int, default=None, help="Override replications per cell")
    parser.add_argument("--cells-limit", type=int, default=None, help="Limit number of cells to run (for testing)")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count() or 4, help="Number of parallel workers")
    parser.add_argument("--output-dir", type=str, default="results/primary", help="Output directory")
    args = parser.parse_args()

    start_time = time.time()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    with open(args.repro_config, "r", encoding="utf-8") as f:
        repro_cfg = yaml.safe_load(f)

    master_seed = int(repro_cfg.get("master_seed", 42))
    replications = args.replications or int(cfg.get("replications_per_cell", 1000))
    n_ref = int(cfg.get("reference_cohort_size", 100000))

    # Pre-compute the 30 clean reference conditions (6 distributions x 5 CEs)
    print(f"Pre-computing reference baselines (Nref = {n_ref:,})...")
    ref_mgr = ReferenceCohortManager(n_ref=n_ref, seed=master_seed)
    ref_cache = {}
    for dist in cfg["distributions"]:
        for ce in cfg["competency_thresholds"]:
            key = (dist, float(ce), 0.60)
            ref_cache[key] = ref_mgr.get_reference(dist, ce, 0.60)
    print("Reference baselines ready.")

    # Build 2,100 primary cell grid
    cells = build_primary_cell_grid(
        cohort_sizes=cfg["cohort_sizes"],
        distributions=cfg["distributions"],
        competency_thresholds=cfg["competency_thresholds"],
        epsilons=cfg["contamination"]["epsilons"],
    )

    if args.cells_limit is not None:
        cells = cells[: args.cells_limit]

    total_cells = len(cells)
    print(f"==================================================")
    print(f"PRIMARY SIMULATION: {total_cells} cells, R = {replications} reps/cell")
    print(f"Workers: {args.n_jobs}, Master Seed: {master_seed}")
    print(f"==================================================")

    all_records: List[Dict[str, Any]] = []

    if args.n_jobs <= 1 or total_cells == 1:
        for cell in tqdm(cells, desc="Simulating cells"):
            cell_res = run_cell_simulation(cell, replications, master_seed, ref_cache)
            all_records.extend(cell_res)
    else:
        tasks = [(cell, replications, master_seed, ref_cache) for cell in cells]
        with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
            futures = [executor.submit(_worker_task, t) for t in tasks]
            for fut in tqdm(as_completed(futures), total=total_cells, desc="Simulating cells"):
                all_records.extend(fut.result())

    df_results = pd.DataFrame(all_records)
    # Sort for deterministic output
    df_results.sort_values(by=["cell_id", "method"], inplace=True)

    # Save cell results
    parquet_path = out_dir / "primary_cell_results.parquet"
    csv_path = out_dir / "primary_cell_results.csv"
    df_results.to_parquet(parquet_path, index=False)
    df_results.to_csv(csv_path, index=False)
    print(f"Saved: {parquet_path} and {csv_path}")

    # Generate summary tables
    summaries = aggregate_primary_summaries(df_results)
    summary_parquet = out_dir / "primary_summary.parquet"
    summary_csv = out_dir / "primary_summary.csv"
    summaries["overall_summary"].to_parquet(summary_parquet, index=False)
    summaries["overall_summary"].to_csv(summary_csv, index=False)

    excel_path = out_dir / "primary_tables.xlsx"
    export_results_to_excel(summaries, str(excel_path))
    print(f"Saved: {summary_parquet} and {excel_path}")

    # Metadata
    elapsed = time.time() - start_time
    meta = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": elapsed,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "master_seed": master_seed,
        "total_cells": total_cells,
        "replications_per_cell": replications,
        "total_cohort_evaluations": total_cells * replications,
        "methods_evaluated": 5,
    }
    with open(out_dir / "primary_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Primary simulation complete in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    from typing import Tuple
    main()
