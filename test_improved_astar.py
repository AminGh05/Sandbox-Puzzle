import heapq
import time
import random
from test_discrete import State, get_successors_discrete
from test_col_solver import solve_col
import itertools

values = [0.0, 0.5, 1.0]
all_cols = list(itertools.product(values, repeat=5))
col_cache = {c: solve_col(c) for c in all_cols}

def improved_h(state: State) -> float:
    if state.is_goal():
        return 0.0

    # Base: col_cache costs for both columns if no more side gates are opened
    # But opening side gates can save at most ~5 per eligible row.
    # What are the eligible rows where side gate can be opened?
    # Either currently {1.0, 0.0}, or could potentially become so.
    # A conservative admissible bound:
    c0_cost = col_cache.get(state.col0, (0.0, 0))[0]
    c1_cost = col_cache.get(state.col1, (0.0, 0))[0]
    independent_sum = c0_cost + c1_cost

    # Number of rows where one is 1.0 and other is 0.0 (or total ones that could be split)
    # Maximum saving per row is bounded by 8.0:
    # So h = max(0, independent_sum - 8.0 * eligible_count)
    eligible = sum(1 for r in range(5) if {state.col0[r], state.col1[r]} == {1.0, 0.0})
    # If no gates are open, at most 'eligible' side gates can be opened right now
    h_val = max(0.0, independent_sum - 8.0 * eligible)
    
    # Also cannot be less than simple gravity bound:
    simple_h = 0.0
    for col, gates in [(state.col0, state.gates0), (state.col1, state.gates1)]:
        if sum(col) > 0:
            simple_h += 3.0
            for r in range(4):
                if sum(col[:r+1]) > 0 and not gates[r]:
                    simple_h += 1.0

    return max(h_val, simple_h)

def solve_astar_fast(initial_state: State):
    counter = 0
    h0 = improved_h(initial_state)
    pq = [(h0, 0.0, counter, initial_state)]
    visited = {initial_state: 0.0}
    parent = {}
    nodes_expanded = 0

    while pq:
        f, g, _, current = heapq.heappop(pq)
        nodes_expanded += 1

        if current.is_goal():
            path = []
            curr = current
            while curr in parent:
                prev_state, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                curr = prev_state
            path.reverse()
            return g, path, nodes_expanded

        if g > visited.get(current, float('inf')):
            continue

        for act, next_st, act_cost in get_successors_discrete(current):
            new_g = g + act_cost
            if next_st not in visited or new_g < visited[next_st]:
                visited[next_st] = new_g
                parent[next_st] = (current, act, act_cost)
                counter += 1
                new_f = new_g + improved_h(next_st)
                heapq.heappush(pq, (new_f, new_g, counter, next_st))

    return None, None, nodes_expanded

print("Testing improved A* on 10 random states...")
random.seed(42)
for i in range(10):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    
    t0 = time.time()
    cost, path, nodes = solve_astar_fast(st)
    dt = time.time() - t0
    print(f"State {i}: Cost={cost}, Nodes={nodes}, Time={dt:.3f}s")
