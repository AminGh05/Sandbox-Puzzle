"""
heuristic_learned.py
====================
Phase 2: Learned admissible heuristic for the Sand Drawer Puzzle.

A linear-regression model
    h_hat(s) = w . phi(s)
is trained on exact optimal cost-to-go values h*(s) collected by
Dijkstra (UCS) full expansions of random initial states.

To (empirically) guarantee admissibility the raw prediction is
post-processed with a calibration constant alpha <= 1 measured on the
training set:

    h_learned(s) = alpha * max(0, w . phi(s))       (weights w >= 0 via NNLS)

The design, features and the admissibility argument are documented in
PHASE2_DOCUMENTATION.md.
"""

import json
import os
from typing import Dict, List, Tuple

from environment import State

WEIGHTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "heuristic_weights.json"
)

# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------
# For each column c with sand vector col and gate vector gates we compute:
#   f_exit  : 1 if column contains sand           (bottom exit needed, cost >= 3)
#   f_gate  : #closed gates with sand above them  (each transit cost >= 1)
#   f_sand  : total sand in the column
#   f_cells : number of cells containing sand
#   f_jam   : number of jammed-open gates         (extra drains usually needed)
#   f_full  : number of full (1.0) cells          (jammed flush potential)
#   f_gap   : sum over rows of min(col0[r], col1[r]) (equalization potential)
# Feature vector phi(s) = [1, sum_c f_*, max_c f_*] per base feature, i.e.
# bias + both a column-sum and a column-max view of each base feature.
# ---------------------------------------------------------------------------

FEATURE_NAMES = (["bias"]
                 + [f"{name}_{agg}"
                    for name in ["exit", "gate", "sand", "cells", "jam", "full", "gap"]
                    for agg in ["sum", "max"]]
                 + [f"{name}2_{agg}"
                    for name in ["gate", "sand", "cells", "full"]
                    for agg in ["sum", "max"]])


def column_features(
    col: Tuple[float, ...], gates: Tuple[bool, ...]
) -> Dict[str, float]:
    R = len(col)
    has_sand = 1.0 if sum(col) > 0.0 else 0.0
    closed_below_sand = 0.0
    for r in range(R - 1):
        if sum(col[: r + 1]) > 0.0 and not gates[r]:
            closed_below_sand += 1.0
    n_cells = sum(1.0 for v in col if v > 0.0)
    n_jammed = sum(1.0 for g in gates if g)
    n_full = sum(1.0 for v in col if v == 1.0)
    return {
        "exit": has_sand,
        "gate": closed_below_sand,
        "sand": sum(col),
        "cells": n_cells,
        "jam": n_jammed,
        "full": n_full,
    }


def extract_features(state: State) -> List[float]:
    cf0 = column_features(state.col0, state.gates0)
    cf1 = column_features(state.col1, state.gates1)
    phi = [1.0]  # bias
    base = {}
    for name in ["exit", "gate", "sand", "cells", "jam", "full"]:
        s = cf0[name] + cf1[name]
        m = max(cf0[name], cf1[name])
        base[name] = (s, m)
        phi.extend([s, m])
    gap = sum(min(state.col0[r], state.col1[r]) for r in range(state.rows))
    base["gap"] = (gap, gap)
    phi.extend([gap, gap])
    # Quadratic expansion of key features (still linear in the weights)
    for name in ["gate", "sand", "cells", "full"]:
        s, m = base[name]
        phi.extend([s * s, m * m])
    return phi


# ---------------------------------------------------------------------------
# Learned heuristic
# ---------------------------------------------------------------------------


class LearnedHeuristic:
    """Linear-regression heuristic with calibration factor for admissibility."""

    def __init__(self, weights: List[float], alpha: float, feature_names: List[str]):
        self.weights = weights
        self.alpha = alpha
        self.feature_names = feature_names
        self.calls = 0

    @classmethod
    def load(cls, path: str = WEIGHTS_FILE) -> "LearnedHeuristic":
        with open(path, "r") as f:
            data = json.load(f)
        return cls(data["weights"], data["alpha"], data["feature_names"])

    def raw(self, state: State) -> float:
        phi = extract_features(state)
        return sum(w * x for w, x in zip(self.weights, phi))

    def __call__(self, state: State) -> float:
        self.calls += 1
        if state.is_goal():
            return 0.0
        return self.alpha * max(0.0, self.raw(state))

    def describe(self) -> str:
        lines = [
            "h_learned(s) = alpha * max(0, w . phi(s))",
            f"alpha = {self.alpha:.6f}",
        ]
        for name, w in zip(self.feature_names, self.weights):
            lines.append(f"  w[{name:<9s}] = {w:+.6f}")
        return "\n".join(lines)


def load_learned_heuristic(path: str = WEIGHTS_FILE) -> LearnedHeuristic:
    return LearnedHeuristic.load(path)
