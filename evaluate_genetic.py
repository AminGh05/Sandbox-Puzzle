"""Reproducible GA vs UCS evaluation on distinct random sand-drawer states.

Example:
    python evaluate_genetic.py --trials 100 --seed 20261127
"""

import argparse
import csv
import json
import math
import os
import time
from statistics import mean
from typing import Dict, List

from environment import create_random_state
from genetic_search import genetic_search
from search_algorithms import ucs


def evaluate(trials: int, seed: int, population_size: int, sequence_length: int,
             generations: int, mutation_rate: float) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    seen = set()
    candidate_seed = seed
    while len(rows) < trials:
        initial = create_random_state(rows=5, seed=candidate_seed)
        candidate_seed += 1
        if initial in seen:
            continue
        seen.add(initial)

        ucs_start = time.perf_counter()
        optimum = ucs(initial)
        ucs_seconds = time.perf_counter() - ucs_start
        if optimum.cost is None:
            raise RuntimeError("UCS did not find a solution for a generated puzzle")

        ga_start = time.perf_counter()
        result = genetic_search(
            initial,
            population_size=population_size,
            sequence_length=sequence_length,
            generations=generations,
            mutation_rate=mutation_rate,
            seed=seed + len(rows),
        )
        ga_seconds = time.perf_counter() - ga_start
        succeeded = result.solution is not None
        ratio = result.cost / optimum.cost if succeeded and optimum.cost > 0 else (
            1.0 if succeeded and optimum.cost == 0 else math.inf
        )
        cells = [*initial.col0, *initial.col1]
        rows.append({
            "trial": len(rows) + 1,
            "initial_seed": candidate_seed - 1,
            "initial_cells": ";".join(f"{value:.1f}" for value in cells),
            "ga_success": succeeded,
            "ga_path_cost": result.cost,
            "ucs_optimum_cost": optimum.cost,
            "cost_ratio": ratio,
            "optimal_cost_match": bool(succeeded and math.isclose(
                result.cost, optimum.cost, rel_tol=0.0, abs_tol=1e-9)),
            "ga_generations": result.generations,
            "ga_best_conflict": result.best_conflict,
            "ga_seconds": ga_seconds,
            "ucs_seconds": ucs_seconds,
            "ucs_nodes_expanded": optimum.nodes_expanded,
        })
        print(f"{len(rows):3d}/{trials}: GA={'success' if succeeded else 'failed':7s} "
              f"GA cost={str(result.cost):>7s} UCS={optimum.cost:7.1f} "
              f"elapsed={ga_seconds:.3f}s", flush=True)
    return rows


def summarize(rows: List[Dict[str, object]], args: argparse.Namespace) -> Dict[str, object]:
    total = len(rows)
    successes = [row for row in rows if row["ga_success"]]
    optimal = [row for row in successes if row["optimal_cost_match"]]
    ratios = [float(row["cost_ratio"]) for row in rows]
    successful_ratios = [float(row["cost_ratio"]) for row in successes]
    all_mean_ratio = mean(ratios) if ratios else math.nan
    success_mean_ratio = mean(successful_ratios) if successful_ratios else None
    return {
        "trials": total,
        "distinct_initial_states": len({row["initial_cells"] for row in rows}),
        "ga_successes": len(successes),
        "ga_success_rate_percent": 100.0 * len(successes) / total,
        "optimal_cost_matches": len(optimal),
        "optimal_matches_percent_of_ga_successes": (
            100.0 * len(optimal) / len(successes) if successes else None
        ),
        "optimal_matches_percent_of_all_trials": 100.0 * len(optimal) / total,
        "mean_cost_ratio_all_trials_failed_as_infinity": (
            all_mean_ratio if math.isfinite(all_mean_ratio) else "Infinity"
        ),
        "mean_cost_ratio_successful_trials": success_mean_ratio,
        "mean_ga_seconds": mean(float(row["ga_seconds"]) for row in rows),
        "mean_ucs_seconds": mean(float(row["ucs_seconds"]) for row in rows),
        "ga_configuration": {
            "population_size": args.population_size,
            "sequence_length": args.sequence_length,
            "generations": args.generations,
            "mutation_rate": args.mutation_rate,
            "seed": args.seed,
        },
        "ratio_convention": (
            "A failed GA run has no solution path_cost, so its ratio is +Infinity. "
            "The all-trial arithmetic mean is therefore +Infinity if any run fails. "
            "The finite conditional mean is reported separately over GA successes. "
            "If both GA and UCS cost zero for an already-solved initial state, the "
            "0/0 ratio is defined as 1.0 because the costs match exactly."
        ),
    }


def write_outputs(rows: List[Dict[str, object]], summary: Dict[str, object], output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "genetic_vs_ucs_trials.csv")
    json_path = os.path.join(output_dir, "genetic_vs_ucs_summary.json")
    report_path = os.path.join(output_dir, "GENETIC_EVALUATION.md")
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2, allow_nan=False)

    all_ratio = summary["mean_cost_ratio_all_trials_failed_as_infinity"]
    success_ratio = summary["mean_cost_ratio_successful_trials"]
    report = f"""# Genetic Algorithm Evaluation: GA vs UCS

## Experimental setup

- Distinct random initial states: {summary['trials']} (5×2; each cell sampled with the project's 0.5 empty, 0.3 full, 0.2 half-full probabilities).
- UCS is the exact cost-optimal reference algorithm.
- GA settings: population={summary['ga_configuration']['population_size']}, chromosome length={summary['ga_configuration']['sequence_length']}, generations={summary['ga_configuration']['generations']}, mutation rate={summary['ga_configuration']['mutation_rate']}, seed={summary['ga_configuration']['seed']}.
- A path is cost-optimal when its GA path cost matches UCS within absolute tolerance 1e-9.

## Results

| Measure | Result |
|---|---:|
| GA successful runs | {summary['ga_successes']} / {summary['trials']} ({summary['ga_success_rate_percent']:.2f}%) |
| GA successes with UCS-optimal path cost | {summary['optimal_cost_matches']} / {summary['ga_successes']} ({'N/A' if summary['optimal_matches_percent_of_ga_successes'] is None else f"{summary['optimal_matches_percent_of_ga_successes']:.2f}%"}) |
| Optimal-cost matches among all trials | {summary['optimal_cost_matches']} / {summary['trials']} ({summary['optimal_matches_percent_of_all_trials']:.2f}%) |
| Mean GA/UCS path-cost ratio, successful runs | {'N/A' if success_ratio is None else f"{success_ratio:.6f}"} |
| Mean GA/UCS path-cost ratio, all trials | {all_ratio if isinstance(all_ratio, str) else f"{all_ratio:.6f}"} |
| Mean runtime per GA instance | {summary['mean_ga_seconds']:.4f} s |
| Mean runtime per UCS instance | {summary['mean_ucs_seconds']:.4f} s |

For a failed GA run, `GA_path_cost / UCS_optimum_path_cost` is undefined because
the GA produced no solution path. To keep the all-trial aggregate mathematically
honest, failed runs are assigned a ratio of +Infinity; consequently, that mean is
+Infinity whenever there is at least one failure. The conditional mean over
successful GA runs is reported separately.

If a generated initial state is already a goal, both costs are zero. Its 0/0
ratio is recorded as 1.0 to represent an exact cost match.

Full per-instance states, costs, ratios, runtimes, and UCS node counts are in
`genetic_vs_ucs_trials.csv`; machine-readable settings and aggregate metrics are
in `genetic_vs_ucs_summary.json`.
"""
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)
    print(f"\nWrote {csv_path}, {json_path}, and {report_path}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261127)
    parser.add_argument("--population-size", type=int, default=60)
    parser.add_argument("--sequence-length", type=int, default=30)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--mutation-rate", type=float, default=0.12)
    parser.add_argument("--output-dir", default="ga_evaluation")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    rows = evaluate(args.trials, args.seed, args.population_size,
                    args.sequence_length, args.generations, args.mutation_rate)
    summary = summarize(rows, args)
    write_outputs(rows, summary, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
