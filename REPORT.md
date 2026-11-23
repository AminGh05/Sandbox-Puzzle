# Phase 2 Evaluation Report

## Reproduction

Use Python 3.10 or newer. Install dependencies with `python -m pip install -r requirements.txt`, then run:

```powershell
python train_heuristic.py
python evaluate_phase2.py 30
```

The evaluator writes `phase2_summary.json` and regenerates the three required charts from the exhaustive phase 1 cache (`all_59049_results.pkl`). It estimates effective branching factor per run and reports aggregates. The optional benchmark argument controls the number of seeded random starts; increase it for a more stable estimate. The exact per-node UCS audit can take substantial time.

## Existing training evidence

The checked-in `train_log.txt` is from 800 seeded random examples. It reports validation MAE 44.206, RMSE 45.761 and R² −13.973, with a calibration factor of approximately 3.62×10⁻¹⁰. Thus the learned estimate is nearly zero and its predictive quality is poor. Calibration constrains only observed training examples; it is not a mathematical admissibility proof for unseen states. Run the training command to refresh `heuristic_weights.json` and the log after code or dependency changes.

## Required figures and metrics

- `histogram_greedy_opt_ratio.png`: frequency distribution over all 59,049 discrete initial sand configurations.
- `scatter_plot1_greedy_vs_opt.png`: greedy solution cost on x and optimum cost on y.
- `scatter_plot2_actions_vs_type_b.png`: solution action count on x and type-b (side gate) count on y.
- `phase2_summary.json`: per-algorithm effective branching factor and run-level costs, expansions, depths and times, plus finite-sample admissibility audit results.

The learned model's admissibility is empirically audited only on expanded nodes in the selected benchmark. For a formal admissibility claim, use the phase 1 `h_gravity` heuristic and its proof in `DOCUMENTATION.md`; non-negative regression weights and finite calibration do not establish a global guarantee.

## Chat transcript

The assignment asks for the complete AI conversation transcript. Export/download this conversation from the chat application and include it alongside the source submission; this repository cannot contain the full prior conversation unless it is explicitly exported into the project.
