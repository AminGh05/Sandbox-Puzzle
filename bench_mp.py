import multiprocessing as mp
import time
import itertools
from test_discrete import State, solve_ucs
from test_improved_astar import solve_astar_fast

def worker_task(pair):
    c0, c1 = pair
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    # Solve with A*
    cost, path, nodes = solve_astar_fast(st)
    num_actions = len(path) if path else 0
    num_b = sum(1 for act, _, _ in path if act.type == 'side') if path else 0
    return (c0, c1, cost, num_actions, num_b)

if __name__ == '__main__':
    values = [0.0, 0.5, 1.0]
    all_cols = list(itertools.product(values, repeat=5))
    
    # Take first 500 pairs
    pairs = []
    for i in range(len(all_cols)):
        for j in range(i, len(all_cols)):
            pairs.append((all_cols[i], all_cols[j]))
            if len(pairs) >= 500:
                break
        if len(pairs) >= 500:
            break
            
    print(f"Testing multiprocessing with {mp.cpu_count()} workers on {len(pairs)} pairs...")
    t0 = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(worker_task, pairs)
    dt = time.time() - t0
    print(f"Solved {len(results)} pairs in {dt:.2f} seconds ({len(results)/dt:.1f} states/sec)!")
