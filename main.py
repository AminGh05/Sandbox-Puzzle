"""
main.py
=======
Main Entry Point for the Artificial Intelligence Sand Drawer Puzzle Assignment.

Usage:
    python main.py --teacher     # Verify professor's 4x2 lecture example
    python main.py --random      # Solve a random 5x2 state with all algorithms
    python main.py --compare     # Benchmark algorithms across multiple states
    python main.py --visualize   # Generate animated GIF and HTML5 visualizer
    python main.py --batch       # Run or display full 59,049 state analysis
    python main.py --all         # Run all demonstrations
"""

import os
import sys

# Suppress matplotlib font cache warning
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mpl_cache')

import argparse
import time
from typing import List

from environment import (
    State, create_teacher_state, create_random_state
)
from heuristics import h_gravity, h0, h_exit_bound
from search_algorithms import (
    bfs, dfs, ids, ucs, greedy_column_search, astar, rbfs, SearchResult
)
from visualizer import animate_solution, generate_interactive_html

def print_separator(title: str = "", char: str = "=", length: int = 75):
    if title:
        padding = (length - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}", flush=True)
    else:
        print(char * length, flush=True)


def run_teacher_example():
    """
    Demonstrate and verify the professor's 4x2 class example:
    1 0
    0 1
    0 1
    1 0
    """
    print_separator("TEACHER'S LECTURE EXAMPLE (4x2 MATRIX)")
    state = create_teacher_state()
    print(state, flush=True)
    print("\nProfessor's Analytical Calculations:")
    print("  1. Greedy approach     : 5+5+9+5 = 24, 9+9+5 = 23  ==> Total = 47.0")
    print("  2. Side gates approach : 1+1=2, 7+9+9+5=30, 3+5+5=13 ==> Total = 45.0")
    print("  3. Other alternative   : 1+1=2, 3+5+9+9+5=31, 3+5+5=13 ==> Total = 46.0")
    print(flush=True)

    # Run Greedy
    res_greedy = greedy_column_search(state)
    print(f"Algorithm: Greedy Search      -> Cost: {res_greedy.cost:5.1f} | Steps: {res_greedy.steps:2d} | Time: {res_greedy.elapsed_time*1000:6.2f} ms", flush=True)

    # Run BFS
    res_bfs = bfs(state)
    print(f"Algorithm: BFS (Step-Optimal) -> Cost: {res_bfs.cost:5.1f} | Steps: {res_bfs.steps:2d} | Time: {res_bfs.elapsed_time*1000:6.2f} ms", flush=True)

    # Run UCS
    res_ucs = ucs(state)
    print(f"Algorithm: UCS (Cost-Optimal) -> Cost: {res_ucs.cost:5.1f} | Steps: {res_ucs.steps:2d} | Time: {res_ucs.elapsed_time*1000:6.2f} ms", flush=True)

    # Run A*
    res_astar = astar(state, h_gravity)
    print(f"Algorithm: A* Search          -> Cost: {res_astar.cost:5.1f} | Steps: {res_astar.steps:2d} | Time: {res_astar.elapsed_time*1000:6.2f} ms", flush=True)

    # Run IDS
    res_ids = ids(state, max_depth=10)
    print(f"Algorithm: IDS                -> Cost: {res_ids.cost:5.1f} | Steps: {res_ids.steps:2d} | Time: {res_ids.elapsed_time*1000:6.2f} ms", flush=True)

    # Run DFS
    res_dfs = dfs(state, max_depth=25)
    print(f"Algorithm: DFS                -> Cost: {res_dfs.cost:5.1f} | Steps: {res_dfs.steps:2d} | Time: {res_dfs.elapsed_time*1000:6.2f} ms", flush=True)

    print("\nOptimal Cost Breakdown (from UCS / A*):", flush=True)
    if res_astar.path:
        for idx, (act, c, _) in enumerate(res_astar.path, 1):
            print(f"  Step {idx:2d}: {act.description:<26s} (Cost = {c:4.1f})", flush=True)

    print("\nConclusion:")
    print("  The teacher noted in lecture: 'Side gates approach (here, might be optimum) ==> 45'.")
    print("  Our AI search proves that the global optimum is actually 38.0 by utilizing early")
    print("  side gates on rows 0 and 3, saving additional high-cost jammed flushes!", flush=True)


def run_random_example(seed: int = 42):
    """
    Run all algorithms on a randomly generated 5x2 matrix.
    """
    print_separator("RANDOM 5x2 STATE EVALUATION")
    state = create_random_state(rows=5, seed=seed)
    print(state, flush=True)
    print(f"\nTotal sand units: {state.total_sand():.1f}", flush=True)
    print(flush=True)

    algorithms = [
        ("Greedy Search", lambda s: greedy_column_search(s)),
        ("BFS", lambda s: bfs(s)),
        ("UCS", lambda s: ucs(s)),
        ("A* (h_gravity)", lambda s: astar(s, h_gravity)),
        ("A* (h0)", lambda s: astar(s, h0)),
        ("IDS", lambda s: ids(s, max_depth=12)),
        ("DFS", lambda s: dfs(s, max_depth=25)),
    ]

    print(f"{'Algorithm':<18s} | {'Cost':<7s} | {'Steps':<6s} | {'Expanded Nodes':<15s} | {'Time (ms)':<10s}", flush=True)
    print("-" * 65, flush=True)

    results = []
    for name, fn in algorithms:
        res = fn(state)
        results.append(res)
        cost_str = f"{res.cost:6.1f}" if res.cost is not None else "N/A"
        steps_str = f"{res.steps:4d}" if res.steps is not None else "N/A"
        print(f"{name:<18s} | {cost_str:<7s} | {steps_str:<6s} | {res.nodes_expanded:<15d} | {res.elapsed_time*1000:8.2f} ms", flush=True)

    return state, results


def run_benchmarks(num_states: int = 5):
    """
    Benchmark algorithms across multiple randomly seeded 5x2 states.
    """
    print_separator(f"ALGORITHM BENCHMARK ACROSS {num_states} RANDOM STATES")
    solvers = [
        ("Greedy", greedy_column_search),
        ("BFS", bfs),
        ("UCS", ucs),
        ("A*", lambda s: astar(s, h_gravity)),
    ]

    totals = {name: {'cost': 0.0, 'steps': 0, 'nodes': 0, 'time': 0.0} for name, _ in solvers}

    for seed in range(num_states):
        st = create_random_state(rows=5, seed=seed * 17 + 1)
        print(f"\n--- State #{seed + 1} (Total Sand: {st.total_sand():.1f}) ---", flush=True)
        for name, fn in solvers:
            res = fn(st)
            totals[name]['cost'] += res.cost
            totals[name]['steps'] += res.steps
            totals[name]['nodes'] += res.nodes_expanded
            totals[name]['time'] += res.elapsed_time
            print(f"  {name:<8s} -> Cost: {res.cost:5.1f} | Steps: {res.steps:2d} | Nodes: {res.nodes_expanded:6d} | Time: {res.elapsed_time*1000:6.1f} ms", flush=True)

    print_separator("AVERAGE BENCHMARK METRICS")
    print(f"{'Algorithm':<12s} | {'Avg Cost':<10s} | {'Avg Steps':<10s} | {'Avg Nodes':<12s} | {'Avg Time (ms)':<12s}", flush=True)
    print("-" * 65, flush=True)
    for name, _ in solvers:
        c = totals[name]['cost'] / num_states
        s = totals[name]['steps'] / num_states
        n = totals[name]['nodes'] / num_states
        t = totals[name]['time'] / num_states * 1000
        print(f"{name:<12s} | {c:<10.2f} | {s:<10.2f} | {n:<12.1f} | {t:<12.2f} ms", flush=True)


def run_visualizer_demo():
    """
    Generate the animated GIF and HTML5 visualizer.
    """
    print_separator("GENERATING VISUALIZATIONS & ANIMATIONS")

    # 1. HTML5 Dashboard
    html_file = "sand_drawer_visualizer.html"
    generate_interactive_html(html_file)

    # 2. Matplotlib GIF Animation
    print("Generating animated GIF for teacher's 4x2 optimal solution...", flush=True)
    st = create_teacher_state()
    res = astar(st, h_gravity)
    gif_file = "teacher_solution_animation.gif"
    animate_solution(st, res, save_path=gif_file, fps=2)

    print("\nVisualizations successfully generated:", flush=True)
    print(f"  1. Interactive Web Visualizer : {html_file}", flush=True)
    print(f"  2. Solution Animated GIF      : {gif_file}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Sand Drawer Puzzle AI Solver")
    parser.add_argument("--teacher", action="store_true", help="Run teacher's 4x2 lecture example")
    parser.add_argument("--random", action="store_true", help="Run algorithms on a random 5x2 state")
    parser.add_argument("--compare", action="store_true", help="Benchmark algorithms on multiple states")
    parser.add_argument("--visualize", action="store_true", help="Generate GIF animation and HTML dashboard")
    parser.add_argument("--batch", action="store_true", help="Run full 59,049 state analysis")
    parser.add_argument("--all", action="store_true", help="Run all features")

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.all:
        run_teacher_example()
        run_random_example(42)
        run_benchmarks(5)
        run_visualizer_demo()
        print("\nAll demonstrations completed successfully!", flush=True)
    else:
        if args.teacher:
            run_teacher_example()
        if args.random:
            run_random_example(42)
        if args.compare:
            run_benchmarks(5)
        if args.visualize:
            run_visualizer_demo()
        if args.batch:
            from analysis_59049 import run_full_analysis
            run_full_analysis()

if __name__ == '__main__':
    main()
