import itertools
import time
from test_col_solver import solve_col
from environment import State, get_successors

# 1. Precompute 243 single column optimal solutions
values = [0.0, 0.5, 1.0]
all_cols = list(itertools.product(values, repeat=5))
col_cache = {c: solve_col(c) for c in all_cols}

def ultra_fast_solve(c0, c1):
    init_st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    
    best_cost = col_cache[c0][0] + col_cache[c1][0]
    best_actions = col_cache[c0][1] + col_cache[c1][1]
    best_b = 0

    import heapq
    counter = 0
    pq = [(0.0, counter, init_st, 0, 0)]
    visited = {init_st: 0.0}

    while pq:
        g, _, curr, n_act, n_b = heapq.heappop(pq)

        terminal_cost = g + col_cache[curr.col0][0] + col_cache[curr.col1][0]
        terminal_act = n_act + col_cache[curr.col0][1] + col_cache[curr.col1][1]

        if terminal_cost < best_cost:
            best_cost = terminal_cost
            best_actions = terminal_act
            best_b = n_b
        elif terminal_cost == best_cost and terminal_act < best_actions:
            best_actions = terminal_act
            best_b = n_b

        if g > visited.get(curr, float('inf')) or g >= best_cost:
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

    return best_cost, best_actions, best_b

print("Testing ultra_fast_solve on hardest state (all 1s)...")
t0 = time.time()
cost, acts, b_acts = ultra_fast_solve((1.0, 1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0, 1.0))
dt = time.time() - t0
print(f"All 1s: Cost = {cost}, Actions = {acts}, Type b = {b_acts} in {dt*1000:.2f} ms")

print("\nTesting on State 5 (the tricky state)...")
t0 = time.time()
cost5, acts5, b5 = ultra_fast_solve((0.5, 1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 0.0, 1.0))
dt5 = time.time() - t0
print(f"State 5: Cost = {cost5}, Actions = {acts5}, Type b = {b5} in {dt5*1000:.2f} ms (True UCS was 49.0)")
