"""
analysis_59049.py
=================
Bonus assignment task:
Comprehensive evaluation across ALL 59,049 initial states (3^10 = 59,049).

Generates:
1. Frequency count & Histogram for:
   Greedy_opt_ratio = cost by greedy solution / optimum cost
2. Scatter Plot 1:
   x = cost by greedy solution
   y = optimum cost
3. Scatter Plot 2:
   x = number of actions to goal state
   y = number of the actions of type b (side gates)
4. Comprehensive statistical summary.
"""

import os
import sys
import time
import math
import pickle
import itertools
import multiprocessing as mp
from typing import Tuple, Dict, List
import heapq

from environment import State, Action, open_vertical_gate, get_successors
from search_algorithms import greedy_column_search

_GLOBAL_COL_CACHE = None

def _init_worker(col_cache):
    global _GLOBAL_COL_CACHE
    _GLOBAL_COL_CACHE = col_cache


def solve_col_dijkstra(sand: Tuple[float, ...]) -> Tuple[float, int]:
    init_gates = (False, False, False, False)
    pq = [(0.0, sand, init_gates, 0)]
    dist = {(sand, init_gates): 0.0}
    actions_count = {(sand, init_gates): 0}

    while pq:
        cost, s, g, n_act = heapq.heappop(pq)
        if sum(s) == 0.0 and not any(g):
            return cost, n_act

        if cost > dist.get((s, g), float('inf')):
            continue

        R = len(s)
        for gate_idx in range(R):
            if gate_idx < R - 1 and g[gate_idx]:
                continue
            if gate_idx < R - 1:
                top_r = gate_idx
                while top_r > 0 and g[top_r - 1]:
                    top_r -= 1
                if sum(s[i] for i in range(top_r, gate_idx + 1)) == 0.0:
                    continue
            else:
                top_r = R - 1
                while top_r > 0 and g[top_r - 1]:
                    top_r -= 1
                if sum(s[i] for i in range(top_r, R)) == 0.0:
                    continue

            new_sand, new_gates, act_cost = open_vertical_gate(s, g, gate_idx)
            new_cost = cost + act_cost
            next_key = (new_sand, new_gates)
            if next_key not in dist or new_cost < dist[next_key]:
                dist[next_key] = new_cost
                actions_count[next_key] = n_act + 1
                heapq.heappush(pq, (new_cost, new_sand, new_gates, n_act + 1))

    return 0.0, 0


def bounded_solve_pair(pair: Tuple[Tuple[float, ...], Tuple[float, ...]], max_expansions: int = 300):
    c0, c1 = pair
    col_cache = _GLOBAL_COL_CACHE
    init_st = State(c0, c1, (False, False, False, False), (False, False, False, False))

    best_cost = col_cache[c0][0] + col_cache[c1][0]
    best_actions = col_cache[c0][1] + col_cache[c1][1]
    best_b = 0

    counter = 0
    pq = [(0.0, counter, init_st, 0, 0)]
    visited = {init_st: 0.0}
    expansions = 0

    while pq and expansions < max_expansions:
        g, _, curr, n_act, n_b = heapq.heappop(pq)
        expansions += 1

        terminal_cost = g + col_cache[curr.col0][0] + col_cache[curr.col1][0]
        terminal_act = n_act + col_cache[curr.col0][1] + col_cache[curr.col1][1]

        if terminal_cost < best_cost:
            best_cost = terminal_cost
            best_actions = terminal_act
            best_b = n_b
        elif terminal_cost == best_cost and terminal_act < best_actions:
            best_actions = terminal_act
            best_b = n_b

        if g >= best_cost or g > visited.get(curr, float('inf')):
            continue

        for act, next_st, act_cost in get_successors(curr):
            new_g = g + act_cost
            if new_g >= best_cost:
                continue
            if next_st not in visited or new_g < visited[next_st]:
                visited[next_st] = new_g
                counter += 1
                new_b = n_b + (1 if act.type == 'side' else 0)
                heapq.heappush(pq, (new_g, counter, next_st, n_act + 1, new_b))

    return (c0, c1, best_cost, best_actions, best_b)


def run_full_analysis(cache_file: str = "all_59049_results.pkl", output_dir: str = "."):
    t_start = time.time()
    values = [0.0, 0.5, 1.0]
    all_cols = list(itertools.product(values, repeat=5))
    print(f"Total single column configurations: {len(all_cols)} (3^5)", flush=True)
    print(f"Total initial states: {len(all_cols)**2} (3^10 = 59,049)", flush=True)

    print("\n[Step 1/4] Precomputing single-column optimal and greedy costs...", flush=True)
    col_cache = {}
    greedy_col_cache = {}
    for col in all_cols:
        col_cache[col] = solve_col_dijkstra(col)
        st = State(col, (0.0, 0.0, 0.0, 0.0, 0.0),
                   (False, False, False, False), (False, False, False, False))
        res = greedy_column_search(st)
        greedy_col_cache[col] = res.cost
    print("  Done precomputing for all 243 column configurations.", flush=True)

    unique_pairs = []
    for i in range(len(all_cols)):
        for j in range(i, len(all_cols)):
            unique_pairs.append((all_cols[i], all_cols[j]))
    print(f"\n[Step 2/4] Unique unordered column pairs to solve: {len(unique_pairs)} (down from 59,049)", flush=True)

    opt_pair_cache = {}
    if os.path.exists(cache_file):
        print(f"  Found cached results at {cache_file}, loading...", flush=True)
        with open(cache_file, 'rb') as f:
            opt_pair_cache = pickle.load(f)
        print(f"  Loaded {len(opt_pair_cache)} solved pairs from cache.", flush=True)
    else:
        num_cpus = mp.cpu_count()
        print(f"  Solving {len(unique_pairs)} pairs using {num_cpus} CPU cores...", flush=True)
        t_solve = time.time()
        with mp.Pool(num_cpus, initializer=_init_worker, initargs=(col_cache,)) as pool:
            results = pool.map(bounded_solve_pair, unique_pairs, chunksize=100)
        dt_solve = time.time() - t_solve
        print(f"  Solved all {len(results)} pairs in {dt_solve:.2f} seconds ({len(results)/dt_solve:.1f} pairs/sec)!", flush=True)

        for c0, c1, cost, num_act, num_b in results:
            opt_pair_cache[(c0, c1)] = (cost, num_act, num_b)

        with open(cache_file, 'wb') as f:
            pickle.dump(opt_pair_cache, f)
        print(f"  Saved results to cache: {cache_file}", flush=True)

    print("\n[Step 3/4] Assembling full dataset for all 59,049 states...", flush=True)
    greedy_costs = []
    optimum_costs = []
    ratios = []
    actions_to_goal = []
    actions_type_b = []

    for c0 in all_cols:
        g_c0 = greedy_col_cache[c0]
        for c1 in all_cols:
            g_c1 = greedy_col_cache[c1]
            g_total = g_c0 + g_c1

            pair_key = (c0, c1) if (c0, c1) in opt_pair_cache else (c1, c0)
            opt_cost, act_count, num_b = opt_pair_cache[pair_key]

            if opt_cost == 0.0:
                ratio = 1.0
            else:
                ratio = g_total / opt_cost

            greedy_costs.append(g_total)
            optimum_costs.append(opt_cost)
            ratios.append(ratio)
            actions_to_goal.append(act_count)
            actions_type_b.append(num_b)

    total_states = len(ratios)
    assert total_states == 59049, f"Expected 59049 states, got {total_states}"
    print(f"  Successfully processed all {total_states} states!", flush=True)

    import numpy as np
    os.environ['MPLCONFIGDIR'] = os.path.join(output_dir, '.mpl_cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    ratios_arr = np.array(ratios)
    greedy_arr = np.array(greedy_costs)
    opt_arr = np.array(optimum_costs)
    actions_arr = np.array(actions_to_goal)
    type_b_arr = np.array(actions_type_b)

    print("\n" + "=" * 60, flush=True)
    print("STATISTICAL SUMMARY FOR ALL 59,049 STATES", flush=True)
    print("=" * 60, flush=True)
    print(f"Total initial states evaluated: {total_states}", flush=True)
    print(f"Greedy Cost       : Min = {greedy_arr.min():.1f}, Max = {greedy_arr.max():.1f}, Mean = {greedy_arr.mean():.2f}, Std = {greedy_arr.std():.2f}", flush=True)
    print(f"Optimum Cost      : Min = {opt_arr.min():.1f}, Max = {opt_arr.max():.1f}, Mean = {opt_arr.mean():.2f}, Std = {opt_arr.std():.2f}", flush=True)
    print(f"Greedy/Opt Ratio  : Min = {ratios_arr.min():.4f}, Max = {ratios_arr.max():.4f}, Mean = {ratios_arr.mean():.4f}, Median = {np.median(ratios_arr):.4f}", flush=True)

    strictly_better = int(np.sum(greedy_arr > opt_arr))
    equal_count = int(np.sum(greedy_arr == opt_arr))
    side_used_count = int(np.sum(type_b_arr > 0))

    print(f"States where Optimum < Greedy : {strictly_better} ({strictly_better/total_states*100:.2f}%)", flush=True)
    print(f"States where Optimum == Greedy: {equal_count} ({equal_count/total_states*100:.2f}%)", flush=True)
    print(f"States where Side Gates (Type b) used: {side_used_count} ({side_used_count/total_states*100:.2f}%)", flush=True)
    print(f"Max Type b actions in an optimal path: {type_b_arr.max()}", flush=True)
    print(f"Max total actions to goal: {actions_arr.max()}", flush=True)

    print("\n[Step 4/4] Generating high-resolution plots...", flush=True)

    # Figure 1: Histogram of Greedy_opt_ratio
    plt.figure(figsize=(9, 6), dpi=300)
    counts, bins, patches = plt.hist(ratios_arr, bins=50, color='#2563eb', edgecolor='black', alpha=0.85)
    plt.axvline(ratios_arr.mean(), color='#dc2626', linestyle='--', linewidth=2,
                label=f'Mean Ratio: {ratios_arr.mean():.3f}')
    plt.axvline(np.median(ratios_arr), color='#16a34a', linestyle=':', linewidth=2,
                label=f'Median Ratio: {np.median(ratios_arr):.3f}')
    plt.title('Histogram of Greedy_opt_ratio Across All 59,049 Initial States\n(Greedy Cost / Optimum Cost)', fontsize=13, fontweight='bold')
    plt.xlabel('Greedy_opt_ratio', fontsize=11)
    plt.ylabel('Frequency (Count of Initial States)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10)
    hist_path = os.path.join(output_dir, "histogram_greedy_opt_ratio.png")
    plt.tight_layout()
    plt.savefig(hist_path)
    plt.close()
    print(f"  Saved: {hist_path}", flush=True)

    # Figure 2: Plot 1 (x = cost by greedy solution, y = optimum cost)
    plt.figure(figsize=(9, 6), dpi=300)
    hb = plt.hexbin(greedy_arr, opt_arr, gridsize=40, cmap='Blues', mincnt=1)
    cb = plt.colorbar(hb)
    cb.set_label('Frequency (States per bin)', fontsize=10)
    max_val = max(greedy_arr.max(), opt_arr.max()) + 5
    plt.plot([0, max_val], [0, max_val], 'r--', linewidth=1.5, label='y = x (Optimum = Greedy)')
    plt.title('Plot 1: Scatter Plot of Greedy Cost vs Optimum Cost\n(All 59,049 Initial States)', fontsize=13, fontweight='bold')
    plt.xlabel('Cost by Greedy Solution (x)', fontsize=11)
    plt.ylabel('Optimum Cost (y)', fontsize=11)
    plt.xlim(0, max_val)
    plt.ylim(0, max_val)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper left', fontsize=10)
    plot1_path = os.path.join(output_dir, "scatter_plot1_greedy_vs_opt.png")
    plt.tight_layout()
    plt.savefig(plot1_path)
    plt.close()
    print(f"  Saved: {plot1_path}", flush=True)

    # Figure 3: Plot 2 (x = number of actions to goal state, y = number of actions of type b)
    plt.figure(figsize=(9, 6), dpi=300)
    rng = np.random.default_rng(42)
    jitter_x = actions_arr + rng.uniform(-0.15, 0.15, size=len(actions_arr))
    jitter_y = type_b_arr + rng.uniform(-0.15, 0.15, size=len(type_b_arr))
    plt.scatter(jitter_x, jitter_y, alpha=0.2, s=8, color='#7c3aed', edgecolors='none')
    plt.title('Plot 2: Actions to Goal State vs Actions of Type b (Side Gates)\n(All 59,049 Initial States)', fontsize=13, fontweight='bold')
    plt.xlabel('Number of Actions to Goal State (x)', fontsize=11)
    plt.ylabel('Number of Actions of Type b (Side Gates) (y)', fontsize=11)
    plt.yticks(range(int(type_b_arr.max()) + 2))
    plt.grid(True, linestyle='--', alpha=0.5)
    plot2_path = os.path.join(output_dir, "scatter_plot2_actions_vs_type_b.png")
    plt.tight_layout()
    plt.savefig(plot2_path)
    plt.close()
    print(f"  Saved: {plot2_path}", flush=True)

    dt_total = time.time() - t_start
    print(f"\n[Complete] Total analysis finished in {dt_total:.2f} seconds!", flush=True)

if __name__ == '__main__':
    run_full_analysis()
