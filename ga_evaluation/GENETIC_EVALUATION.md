# Genetic Algorithm Evaluation: GA vs UCS

## Experimental setup

- Distinct random initial states: 100 (5×2; each cell sampled with the project's 0.5 empty, 0.3 full, 0.2 half-full probabilities).
- UCS is the exact cost-optimal reference algorithm.
- GA settings: population=60, chromosome length=30, generations=200, mutation rate=0.12, seed=20261127.
- A path is cost-optimal when its GA path cost matches UCS within absolute tolerance 1e-9.

## Results

| Measure | Result |
|---|---:|
| GA successful runs | 100 / 100 (100.00%) |
| GA successes with UCS-optimal path cost | 9 / 100 (9.00%) |
| Optimal-cost matches among all trials | 9 / 100 (9.00%) |
| Mean GA/UCS path-cost ratio, successful runs | 1.160454 |
| Mean GA/UCS path-cost ratio, all trials | 1.160454 |
| Mean runtime per GA instance | 3.1594 s |
| Mean runtime per UCS instance | 2.3355 s |

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
