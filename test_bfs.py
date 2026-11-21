from collections import deque
from test_discrete import State, get_successors_discrete

def solve_bfs(initial_state: State):
    queue = deque([initial_state])
    visited = {initial_state: 0}
    parent = {}
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        nodes_expanded += 1

        if current.is_goal():
            path = []
            curr = current
            total_cost = 0.0
            while curr in parent:
                prev_state, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                total_cost += act_cost
                curr = prev_state
            path.reverse()
            return total_cost, path, nodes_expanded

        for act, next_st, act_cost in get_successors_discrete(current):
            if next_st not in visited:
                visited[next_st] = visited[current] + 1
                parent[next_st] = (current, act, act_cost)
                queue.append(next_st)

    return None, None, nodes_expanded

# Teacher example
init_state = State(
    col0=(1.0, 0.0, 0.0, 1.0),
    col1=(0.0, 1.0, 1.0, 0.0),
    gates0=(False, False, False),
    gates1=(False, False, False)
)

cost, path, nodes = solve_bfs(init_state)
print(f"BFS: Steps = {len(path)}, Total cost = {cost}, Nodes = {nodes}")
for act, c, s in path:
    print(f"  {act.description} (cost={c})")
