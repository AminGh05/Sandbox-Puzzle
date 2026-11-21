import heapq
import time
import random
from test_discrete import State, get_successors_discrete

def compute_h(state: State) -> float:
    if state.is_goal():
        return 0.0
    R = len(state.col0)
    h = 0.0
    for col, gates in [(state.col0, state.gates0), (state.col1, state.gates1)]:
        if sum(col) == 0.0:
            continue
        col_h = 3.0
        for r in range(R - 1):
            if sum(col[:r+1]) > 0 and not gates[r]:
                col_h += 1.0
        h += col_h
    return h

def solve_astar(initial_state: State):
    counter = 0
    h0 = compute_h(initial_state)
    pq = [(h0, 0.0, counter, initial_state)] # (f, g, counter, state)
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
                new_f = new_g + compute_h(next_st)
                heapq.heappush(pq, (new_f, new_g, counter, next_st))

    return None, None, nodes_expanded

print("Testing A* vs UCS...")
random.seed(42)
for i in range(5):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    
    t0 = time.time()
    cost_a, path_a, nodes_a = solve_astar(st)
    dt_a = time.time() - t0
    
    print(f"State {i}: Cost={cost_a}, Nodes={nodes_a}, Time={dt_a:.3f}s")
