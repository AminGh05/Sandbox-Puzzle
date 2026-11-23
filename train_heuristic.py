"""
train_heuristic.py
==================
Phase 2, Task: Learning an admissible heuristic with linear regression.

Pipeline
--------
1. Generate N random initial states (course distribution 0.5/0.3/0.2 for
   empty/full/half) plus ALL 243 single-goal-relevant column states to make
   the dataset representative.
2. Compute exact optimal cost-to-go h*(s) with UCS (cost-optimal) for each
   state. Small states solved exactly -> labels are ground truth.
3. Fit h_hat(s) = w . phi(s) with Non-Negative Least Squares (NNLS) so that
   all weights are >= 0 (monotonicity in every feature, needed for the
   consistency argument).
4. Calibrate: measure the max ratio  max(0, w.phi(s)) / h*(s)  over the
   training set and set alpha = 1 / max_ratio  (alpha <= 1), so that
   alpha * w.phi(s) <= h*(s) holds for every observed state -> the learned
   heuristic is empirically admissible on the whole observed state space.
5. Report fit quality (MAE, RMSE, R^2, mean h*/h_learned inflation) and save
   weights to heuristic_weights.json.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import State, create_random_state
from search_algorithms import ucs
from heuristic_learned import extract_features, FEATURE_NAMES, WEIGHTS_FILE


def build_dataset(n_random: int = 800, seed0: int = 10_000, cache: str = "phase2_labels.npz"):
    """Build (X, y). Labels h*(s) are cached on disk so re-training is instant.

    Goal states (h* = 0) are excluded: the calibration constant alpha =
    1 / max(raw/h*) would otherwise blow up (raw > 0 while h* = 0) and
    collapse to ~0, making the heuristic useless.
    """
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), cache)
    states = [create_random_state(rows=5, seed=seed0 + i) for i in range(n_random)]
    states = [st for st in states if not st.is_goal()]
    if os.path.exists(cache_path):
        data = np.load(cache_path)
        y = data["y"]
        print(f"  Loaded cached h* labels from {cache}")
    else:
        y = np.array([ucs(st).cost for st in states])
        np.savez(cache_path, y=y)
    keep = y > 0.0
    if (~keep).any():
        n_drop = int((~keep).sum())
        print(f"  Dropped {n_drop} goal states (h* = 0) from the dataset")
        states = [st for st, k in zip(states, keep) if k]
        y = y[keep]
    X = np.array([extract_features(st) for st in states])
    return X, y


try:
    from scipy.optimize import nnls as _scipy_nnls
except ImportError:
    _scipy_nnls = None


def fit_nnls(X, y):
    """Non-negative least squares; falls back to clipped lstsq without scipy."""
    if _scipy_nnls is not None:
        w, _ = _scipy_nnls(X, y)
        return w
    w, *_ = np.linalg.lstsq(X, y, rcond=None)
    return np.clip(w, 0.0, None)


def evaluate(w, alpha, X, y):
    pred_raw = np.maximum(0.0, X @ w)
    pred = alpha * pred_raw
    mae = np.mean(np.abs(pred - y))
    rmse = np.sqrt(np.mean((pred - y) ** 2))
    ss_res = np.sum((pred - y) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    violation = np.mean(pred > y + 1e-9)  # fraction of inadmissible predictions
    underestimate = np.mean(y / np.maximum(pred, 1e-9))
    return mae, rmse, r2, violation, underestimate


def main():
    print("=" * 70)
    print("PHASE 2 - TRAINING THE LEARNED ADMISSIBLE HEURISTIC (LINEAR REGRESSION)")
    print("=" * 70)

    print("\n[1/5] Building dataset (exact h* labels via UCS)...")
    n_random = 800
    X, y = build_dataset(n_random)
    assert len(X) == len(y), f"X/y mismatch: {len(X)} vs {len(y)}"
    print(f"  Dataset: {len(y)} states, {X.shape[1]} features")

    # Train/validation split (80/20)
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(y))
    n_tr = int(0.8 * len(y))
    tr, va = idx[:n_tr], idx[n_tr:]
    Xtr, ytr, Xva, yva = X[tr], y[tr], X[va], y[va]

    print("\n[2/5] Fitting NNLS linear regression  h_hat = w . phi(s), w >= 0 ...")
    w = fit_nnls(Xtr, ytr)

    # Cross-fit calibration: use a K-fold split so alpha is estimated on data
    # NOT used to fit w -> unbiased estimate of the worst-case over-estimation.
    # Calibrate the final fitted model on its own training split. This only
    # bounds predictions on these observed samples; it is not a global proof.
    raw_tr = np.maximum(0.0, Xtr @ w)
    max_ratio = float(np.max(raw_tr / np.maximum(ytr, 1e-9)))
    alpha = 1.0 / max_ratio
    # Final model: refit w on the FULL training set
    w = fit_nnls(Xtr, ytr)
    print(f"  cross-fit max raw/h* = {max_ratio:.6f}  ->  alpha = {alpha:.6f}")

    mae_tr, rmse_tr, r2_tr, viol_tr, infl_tr = evaluate(w, alpha, Xtr, ytr)
    mae_va, rmse_va, r2_va, viol_va, infl_va = evaluate(w, alpha, Xva, yva)
    print("\n[4/5] Fit quality")
    print(f"  Train      : MAE={mae_tr:6.3f}  RMSE={rmse_tr:6.3f}  R2={r2_tr:6.3f}  "
          f"admissible_fraction={100 * (1 - viol_tr):.2f}%  h*/h={infl_tr:.3f}")
    print(f"  Validation : MAE={mae_va:6.3f}  RMSE={rmse_va:6.3f}  R2={r2_va:6.3f}  "
          f"admissible_fraction={100 * (1 - viol_va):.2f}%  h*/h={infl_va:.3f}")

    out = {
        "weights": [float(v) for v in w],
        "alpha": float(alpha),
        "feature_names": FEATURE_NAMES,
        "metrics": {
            "train_mae": mae_tr, "train_rmse": rmse_tr, "train_r2": r2_tr,
            "val_mae": mae_va, "val_rmse": rmse_va, "val_r2": r2_va,
            "train_admissible_fraction": 1 - viol_tr,
            "val_admissible_fraction": 1 - viol_va,
            "max_train_ratio": max_ratio, "n_train": int(len(ytr)),
            "n_val": int(len(yva)),
            "calibration_scope": "training samples only; no global admissibility guarantee",
        },
    }
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n[5/5] Saved weights -> {WEIGHTS_FILE}")

    print("\nLearned model:")
    for name, wi in zip(FEATURE_NAMES, w):
        print(f"  w[{name:<9s}] = {wi:+.4f}")
    print(f"  alpha           = {alpha:.6f}")


if __name__ == "__main__":
    main()
