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
