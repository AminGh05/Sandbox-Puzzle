"""
evaluate_phase2.py
==================
Phase 2, Task: Evaluation & performance metrics for the learned heuristic
and the A* algorithm.

Outputs
-------
1. Effective branching factor  b*  estimation:
   For A* with each heuristic we count expanded nodes N and solution depth d,
   then numerically invert      N + 1 = 1 + b* + b*^2 + ... + b*^d
   to get b*. Reported over a benchmark suite of random states, plus
   aggregate mean values.
2. Algorithm comparison table: UCS (h=0) vs A* (h_gravity) vs A* (h_learned)
   vs Greedy: cost, steps, expanded nodes, time.
3. Empirical admissibility audit of h_learned on the benchmark states:
   for every expanded node we verify h(n) <= h*(n) using the exact optimal
   cost-to-go obtained by running UCS from that node.
4. Histogram of Greedy_opt_ratio, scatter plots (greedy vs optimum cost,
   actions vs type-b actions) regenerated from the Phase-1 cached dataset
   (or recomputed if the cache is absent).
"""

import json
import os
import sys
import time
import heapq
from typing import Dict, List

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mpl_cache"),
)

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import State, create_random_state, get_successors
from search_algorithms import SearchResult, astar, ucs, greedy_column_search
from heuristics import h_gravity
from heuristic_learned import load_learned_heuristic, extract_features

BASE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# 1. Effective branching factor
# ---------------------------------------------------------------------------


def total_nodes(b: float, d: int) -> float:
    """1 + b + b^2 + ... + b^d"""
    if b == 1.0:
        return d + 1.0
    return (b ** (d + 1) - 1.0) / (b - 1.0)


def effective_branching_factor(n_expanded: int, depth: int) -> float:
    """Numerically invert total_nodes(b, d) = n_expanded (+1 for root)."""
    target = n_expanded + 1.0
    lo, hi = 1e-6, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if total_nodes(mid, depth) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# 2. Exact cost-to-go oracle for admissibility auditing
# ---------------------------------------------------------------------------


def exact_hstar(state: State) -> float:
    res = ucs(state)
    return res.cost if res.cost is not None else float("inf")


def run_astar_with_audit(state: State, heuristic):
    """A* that additionally checks admissibility of h on every expanded node
    against the exact h* obtained from UCS."""
    t0 = time.time()
    counter = 0
    h0v = heuristic(state)
    pq = [(h0v, 0.0, counter, state)]
    best_g = {state: 0.0}
    parent = {}
    expanded = 0
    violations = 0
    audited = 0

    while pq:
        f, g, _, current = heapq.heappop(pq)
        if g > best_g.get(current, float("inf")):
            continue
        expanded += 1
        if current.is_goal():
            path = []
            curr = current
            while curr in parent:
                prev_st, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                curr = prev_st
            path.reverse()
            return {
                "cost": g,
                "steps": len(path),
                "path": path,
                "nodes": expanded,
                "time": time.time() - t0,
                "h_violations": violations,
                "h_audited": audited,
            }
        hstar_here = exact_hstar(current)
        audited += 1
        h_here = heuristic(current)
        if h_here > hstar_here + 1e-6:
            violations += 1
        for act, nxt, cost in get_successors(current):
            ng = g + cost
            if ng < best_g.get(nxt, float("inf")):
                best_g[nxt] = ng
                parent[nxt] = (current, act, cost)
                counter += 1
                heapq.heappush(pq, (ng + heuristic(nxt), ng, counter, nxt))
    return None


# ---------------------------------------------------------------------------
# 3. Benchmark suite
# ---------------------------------------------------------------------------


def run_benchmark(n_states: int = 30, seed0: int = 900):
    try:
        h_learned = load_learned_heuristic()
        print(f"Loaded learned heuristic: alpha = {h_learned.alpha:.6f}")
        print(h_learned.describe())
    except FileNotFoundError:
        print("heuristic_weights.json not found - run train_heuristic.py first!")
        sys.exit(1)

    rows = []
    total_viol = 0
    total_audit = 0
    print(
        f"\n{'#':>3} | {'alg':<14} | {'cost':>6} | {'steps':>5} | "
        f"{'nodes':>7} | {'d':>3} | {'b*':>6} | {'ms':>8}"
    )
    print("-" * 70)

    for i in range(n_states):
        st = create_random_state(rows=5, seed=seed0 + i)
        if st.is_goal():
            continue
        opt = exact_hstar(st)

        for name, fn in [
            ("A* h_learned", lambda s: astar(s, h_learned)),
            ("A* h_gravity", lambda s: astar(s, h_gravity)),
            ("UCS (h=0)", lambda s: ucs(s)),
            ("Greedy", lambda s: greedy_column_search(s)),
        ]:
            res = fn(st)
            d = res.steps or 0
            bstar = effective_branching_factor(res.nodes_expanded, d)
            rows.append(
                {
                    "state": seed0 + i,
                    "alg": name,
                    "cost": res.cost,
                    "steps": res.steps,
                    "nodes": res.nodes_expanded,
                    "bstar": bstar,
                    "time_ms": res.elapsed_time * 1000,
                    "opt_cost": opt,
                }
            )
            print(
                f"{i:>3} | {name:<14} | {res.cost:>6.1f} | {res.steps:>5} | "
                f"{res.nodes_expanded:>7} | {d:>3} | {bstar:>6.3f} | "
                f"{res.elapsed_time*1000:>8.2f}"
            )

        audit = run_astar_with_audit(st, h_learned)
        total_viol += audit["h_violations"]
        total_audit += audit["h_audited"]
        ratio = (audit["cost"] / opt) if opt > 0 else 1.0
        assert (
            abs(ratio - 1.0) < 1e-6
        ), f"A* with learned h not optimal on state {seed0+i}!"

    return rows, total_viol, total_audit


def summarize(rows: List[Dict], total_viol: int, total_audit: int, out_prefix: str):
    print("\n" + "=" * 70)
    print("PHASE 2 EVALUATION SUMMARY")
    print("=" * 70)

    algs = ["A* h_learned", "A* h_gravity", "UCS (h=0)", "Greedy"]
    n_states = 0
    print(
        f"\n{'Algorithm':<15} | {'mean cost':>9} | {'mean nodes':>10} | "
        f"{'mean b*':>8} | {'mean ms':>8}"
    )
    print("-" * 62)
    bstar_report = {}
    for alg in algs:
        rr = [r for r in rows if r["alg"] == alg]
        n_states = len(rr)
        mc = np.mean([r["cost"] for r in rr])
        mn = np.mean([r["nodes"] for r in rr])
        mb = np.mean([r["bstar"] for r in rr])
        mt = np.mean([r["time_ms"] for r in rr])
        bstar_report[alg] = {
            "mean_bstar": mb,
            "min_bstar": min(r["bstar"] for r in rr),
            "max_bstar": max(r["bstar"] for r in rr),
            "mean_nodes": mn,
            "mean_depth": np.mean([r["steps"] for r in rr]),
        }
        print(f"{alg:<15} | {mc:>9.2f} | {mn:>10.1f} | {mb:>8.4f} | {mt:>8.2f}")

    print(
        f"\nA* with h_learned remained cost-optimal on all {n_states} benchmark states."
    )
    print(
        f"Admissibility audit: {total_audit} nodes audited, "
        f"{total_viol} h-violations "
        f"({100*total_viol/max(total_audit,1):.3f}% inadmissible estimates)."
    )

    report = {
        "effective_branching_factor": bstar_report,
        "admissibility_audit": {"nodes_audited": total_audit, "violations": total_viol},
        "per_state": rows,
    }
    out_json = os.path.join(BASE, f"{out_prefix}_summary.json")
    with open(out_json, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved: {out_json}")


# ---------------------------------------------------------------------------
# 4. Regenerate the required plots from the Phase-1 dataset
# ---------------------------------------------------------------------------


def make_plots():
    pkl = os.path.join(BASE, "all_59049_results.pkl")
    if not os.path.exists(pkl):
        print(
            "\n[plots] cache pickle missing - skipping plot regeneration "
            "(plots already exist in repo)."
        )
        return
    import pickle
    import itertools

    with open(pkl, "rb") as f:
        opt_pair = pickle.load(f)

    values = [0.0, 0.5, 1.0]
    cols = list(itertools.product(values, repeat=5))
    from analysis_59049 import solve_col_dijkstra
    from search_algorithms import greedy_column_search
    from environment import State as S

    greedy_costs, opt_costs, ratios, acts, tb = [], [], [], [], []
    greedy_cache = {}
    for col in cols:
        st = S(col, tuple([0.0] * 5), tuple([False] * 4), tuple([False] * 4))
        greedy_cache[col] = greedy_column_search(st).cost
    for (c0, c1), (oc, na, nb) in opt_pair.items():
        g = greedy_cache[c0] + greedy_cache[c1]
        r = g / oc if oc > 0 else 1.0
        greedy_costs.append(g)
        opt_costs.append(oc)
        ratios.append(r)
        acts.append(na)
        tb.append(nb)

    g = np.array(greedy_costs)
    o = np.array(opt_costs)
    r = np.array(ratios)
    a = np.array(acts)
    b = np.array(tb)
    print(f"\n[plots] {len(r)} states")

    # Histogram
    plt.figure(figsize=(9, 6), dpi=200)
    plt.hist(r, bins=50, color="#2563eb", edgecolor="black", alpha=0.85)
    plt.axvline(
        r.mean(), color="#dc2626", ls="--", lw=2, label=f"Mean = {r.mean():.4f}"
    )
    plt.axvline(
        np.median(r),
        color="#16a34a",
        ls=":",
        lw=2,
        label=f"Median = {np.median(r):.4f}",
    )
    plt.title("Greedy_opt_ratio = Greedy Cost / Optimum Cost (59,049 states)")
    plt.xlabel("Greedy_opt_ratio")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(alpha=0.4, ls="--")
    plt.tight_layout()
    plt.savefig(os.path.join(BASE, "histogram_greedy_opt_ratio.png"))
    plt.close()

    # Scatter 1
    plt.figure(figsize=(9, 6), dpi=200)
    hb = plt.hexbin(g, o, gridsize=40, cmap="Blues", mincnt=1)
    plt.colorbar(hb, label="States per bin")
    m = max(g.max(), o.max()) + 5
    plt.plot([0, m], [0, m], "r--", label="y = x")
    plt.xlabel("Cost by Greedy Solution (x)")
    plt.ylabel("Optimum Cost (y)")
    plt.title("Greedy Cost vs Optimum Cost (59,049 states)")
    plt.legend()
    plt.grid(alpha=0.4, ls="--")
    plt.tight_layout()
    plt.savefig(os.path.join(BASE, "scatter_plot1_greedy_vs_opt.png"))
    plt.close()

    # Scatter 2
    rng = np.random.default_rng(42)
    plt.figure(figsize=(9, 6), dpi=200)
    plt.scatter(
        a + rng.uniform(-0.15, 0.15, len(a)),
        b + rng.uniform(-0.15, 0.15, len(b)),
        alpha=0.2,
        s=8,
        color="#7c3aed",
        edgecolors="none",
    )
    plt.xlabel("Number of Actions to Goal State (x)")
    plt.ylabel("Number of Actions of Type b (y)")
    plt.title("Actions to Goal vs Type-b (Side Gate) Actions (59,049 states)")
    plt.yticks(range(int(b.max()) + 2))
    plt.grid(alpha=0.4, ls="--")
    plt.tight_layout()
    plt.savefig(os.path.join(BASE, "scatter_plot2_actions_vs_type_b.png"))
    plt.close()
    print("[plots] saved histogram + 2 scatter plots")


def main():
    n_states = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rows, viol, audit = run_benchmark(n_states)
    summarize(rows, viol, audit, "phase2")
    make_plots()


if __name__ == "__main__":
    main()
