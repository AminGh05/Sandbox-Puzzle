from test_discrete import State, get_successors_discrete

def solve_dls(state: State, limit: int, path: list, visited_in_path: set):
    if state.is_goal():
        return True, path, 1

    if limit <= 0:
        return False, None, 1

    nodes = 1
    for act, next_st, act_cost in get_successors_discrete(state):
        if next_st in visited_in_path:
            continue
        visited_in_path.add(next_st)
        path.append((act, act_cost, next_st))
        found, sol_path, n = solve_dls(next_st, limit - 1, path, visited_in_path)
        nodes += n
        if found:
            return True, sol_path, nodes
        path.pop()
        visited_in_path.remove(next_st)

    return False, None, nodes

def solve_ids(initial_state: State, max_depth: int = 20):
    total_nodes = 0
    for depth in range(max_depth + 1):
        visited_in_path = {initial_state}
        found, path, nodes = solve_dls(initial_state, depth, [], visited_in_path)
        total_nodes += nodes
        if found:
            total_cost = sum(c for _, c, _ in path)
            return total_cost, path, total_nodes, depth
    return None, None, total_nodes, max_depth

# Teacher example
init_state = State(
    col0=(1.0, 0.0, 0.0, 1.0),
    col1=(0.0, 1.0, 1.0, 0.0),
    gates0=(False, False, False),
    gates1=(False, False, False)
)

cost, path, nodes, depth = solve_ids(init_state)
print(f"IDS: Found at depth {depth}, Steps = {len(path)}, Total cost = {cost}, Nodes = {nodes}")
for act, c, s in path:
    print(f"  {act.description} (cost={c})")
