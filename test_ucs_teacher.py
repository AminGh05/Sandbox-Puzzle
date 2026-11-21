import heapq
import time
from sand_drawer import State, get_successors

def solve_ucs(initial_state: State):
    counter = 0
    pq = [(0.0, counter, initial_state)]
    visited = {initial_state: 0.0}
    parent = {}

    nodes_expanded = 0

    while pq:
        cost, _, current = heapq.heappop(pq)
        nodes_expanded += 1

        if current.is_goal():
            # Reconstruct path
            path = []
            curr = current
            while curr in parent:
                prev_state, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                curr = prev_state
            path.reverse()
            return cost, path, nodes_expanded

        if cost > visited.get(current, float('inf')):
            continue

        for act, next_st, act_cost in get_successors(current):
            new_cost = cost + act_cost
            if next_st not in visited or new_cost < visited[next_st]:
                visited[next_st] = new_cost
                parent[next_st] = (current, act, act_cost)
                counter += 1
                heapq.heappush(pq, (new_cost, counter, next_st))

    return None, None, nodes_expanded

init_state = State(
    col0=(1.0, 0.0, 0.0, 1.0),
    col1=(0.0, 1.0, 1.0, 0.0),
    gates0=(False, False, False),
    gates1=(False, False, False)
)

t0 = time.time()
cost, path, nodes = solve_ucs(init_state)
dt = time.time() - t0
print(f"Optimal cost: {cost} in {dt:.3f}s (expanded {nodes} nodes)")
if path:
    print("Actions:")
    for act, c, st in path:
        print(f"  {act.description} (cost={c})")
