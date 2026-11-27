# Sand Drawer Puzzle — Phase 2

Phase 2 adds a learned linear heuristic, A* evaluation, and required metrics/plots to the phase 1 simulator.

## Setup and run

```powershell
python -m pip install -r requirements.txt
python train_heuristic.py
python evaluate_phase2.py 30
```

See [PHASE2_DOCUMENTATION.md](PHASE2_DOCUMENTATION.md) for design and [REPORT.md](REPORT.md) for metric definitions, current training evidence, and reproducibility notes. The exact-optimal training labels are cached in `phase2_labels.npz`; the exhaustive phase 1 result cache is `all_59049_results.pkl`.

The model calibration is empirical and does not prove admissibility on unseen states. Refer to the report for this limitation and the current model's poor fit.

## Genetic search over action sequences

The workshop genetic algorithm treats each chromosome as a fixed-length list of
sand-drawer actions. Every chromosome is replayed from the same initial board;
replay stops at the first goal. Unsuccessful chromosomes are ranked by their
lowest conflict number reached (remaining sand plus open gates) and path cost.
Illegal actions score zero. The default sequence length is 30, and the population
size must be even.

```powershell
python main.py --genetic --population-size 60 --sequence-length 30 --generations 200 --seed 42
```

The scoring and operators can also be used directly from `genetic_search.py`:
`evaluate_sequence`, `successful_path`, `conflict_number`, and `genetic_search`.
The successful-path bonus is a hyperparameter (`success_bonus`, default 1000);
unsuccessful fitness uses the best conflict and accumulated path cost.

## Assignment report and evaluation

See [GA_PROJECT_REPORT.md](GA_PROJECT_REPORT.md) for the seven design steps,
fitness rationale, genetic operators, and evaluation protocol. Run the required
100 distinct-instance comparison against exact UCS with:

```powershell
./run_ga_evaluation.ps1
```

Or configure it directly with `python evaluate_genetic.py --trials 100 ...`.
The run writes a per-instance CSV, a JSON summary, and a Markdown report under
`ga_evaluation/`.

Recorded run (seed `20261127`, 100 distinct boards): GA solved 100/100, matched
UCS cost on 9/100, and had a mean cost ratio of 1.160454. See
[`ga_evaluation/GENETIC_EVALUATION.md`](ga_evaluation/GENETIC_EVALUATION.md)
and its per-instance CSV for the full results.
