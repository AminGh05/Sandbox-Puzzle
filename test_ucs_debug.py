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
        if nodes_expanded % 1000 == 0:
            print(f"Nodes: {nodes_expanded}, cost: {cost}, pq_size: {len(pq)}, visited: {len(visited)}", flush=True)

        if current.is_goal():
            return cost, nodes_expanded

        if cost > visited.get(current, float('inf')):
            continue

        for act, next_st, act_cost in get_successors(current):
            new_cost = cost + act_cost
            if next_st not in visited or new_cost < visited[next_st]:
                visited[next_st] = new_cost
                parent[next_st] = (current, act, act_cost)
                counter += 1
                heapq.heappush(pq, (new_cost, counter, next_st))

    return None, nodes_expanded

init_state = State(
    col0=(1.0, 0.0, 0.0, 1.0),
    col1=(0.0, 1.0, 1.0, 0.0),
    gates0=(False, False, False),
    gates1=(False, False, False)
)

print("Starting UCS...")
cost, nodes = solve_ucs(init_state)
print("Done! Cost:", cost, "Nodes:", nodes)
