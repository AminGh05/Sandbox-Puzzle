# Updating dfs in search_algorithms.py to use global visited set:
"""
def dfs(initial_state: State, max_depth: int = 30) -> SearchResult:
    t0 = time.time()
    stack = [(initial_state, [])]
    visited: Set[State] = {initial_state}
    nodes_expanded = 0

    while stack:
        current, path = stack.pop()
        nodes_expanded += 1

        if current.is_goal():
            total_cost = sum(c for _, c, _ in path)
            return SearchResult("DFS", total_cost, len(path), path, nodes_expanded, time.time() - t0)

        if len(path) >= max_depth:
            continue

        for act, next_st, act_cost in reversed(get_successors(current)):
            if next_st not in visited:
                visited.add(next_st)
                stack.append((next_st, path + [(act, act_cost, next_st)]))

    return SearchResult("DFS", None, None, None, nodes_expanded, time.time() - t0)
"""
