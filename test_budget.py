import itertools
import time
from test_col_solver import solve_col
from environment import State, get_successors

values = [0.0, 0.5, 1.0]
all_cols = list(itertools.product(values, repeat=5))
col_cache = {c: solve_col(c) for c in all_cols}

def bounded_solve_pair(c0, c1, max_expansions=300):
    init_st = State(c0, c1, (False, False, False, False), (False, False, False, False))

    best_cost = col_cache[c0][0] + col_cache[c1][0]
    best_actions = col_cache[c0][1] + col_cache[c1][1]
    best_b = 0

    import heapq
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

print("Testing bounded solve on All 1s...")
t0 = time.time()
res_all1 = bounded_solve_pair((1.0, 1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0, 1.0), 300)
print("All 1s solved in", time.time() - t0, "s:", res_all1[2:])

print("Testing bounded solve on State 5...")
t0 = time.time()
res_s5 = bounded_solve_pair((0.5, 1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 0.0, 1.0), 300)
print("State 5 solved in", time.time() - t0, "s:", res_s5[2:])
