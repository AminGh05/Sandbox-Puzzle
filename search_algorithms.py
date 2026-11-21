"""
search_algorithms.py
====================
Implementations of all required search algorithms for the Sand Drawer puzzle:
1. BFS (Breadth-First Search) - Step-optimal
2. DFS (Depth-First Search)
3. IDS (Iterative Deepening Search) - Step-optimal, O(bd) space
4. Uniform-Cost Search (UCS / Dijkstra) - Cost-optimal
5. Custom Greedy Column Search - Teacher's approach
6. A* Search - Cost-optimal heuristic search
7. RBFS (Recursive Best-First Search) - Linear-space heuristic search
"""

import heapq
import time
from collections import deque
from typing import List, Tuple, Optional, Callable, NamedTuple, Set
from environment import State, Action, get_successors, open_vertical_gate
from heuristics import h_gravity

class SearchResult(NamedTuple):
    algorithm: str
    cost: Optional[float]
    steps: Optional[int]
    path: Optional[List[Tuple[Action, float, State]]]
    nodes_expanded: int
    elapsed_time: float


# ==========================================
# 1. Breadth-First Search (BFS)
# ==========================================
def bfs(initial_state: State) -> SearchResult:
    """
    Breadth-First Search:
    Explores shallowest unexpanded nodes first using a FIFO queue.
    Guarantees finding the solution with the minimum number of actions (step-optimal).
    """
    t0 = time.time()
    if initial_state.is_goal():
        return SearchResult("BFS", 0.0, 0, [], 1, time.time() - t0)

    queue = deque([initial_state])
    visited: Set[State] = {initial_state}
    parent = {} # state -> (prev_state, action, cost)
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        nodes_expanded += 1

        if current.is_goal():
            path = []
            curr = current
            total_cost = 0.0
            while curr in parent:
                prev_st, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                total_cost += act_cost
                curr = prev_st
            path.reverse()
            return SearchResult("BFS", total_cost, len(path), path, nodes_expanded, time.time() - t0)

        for act, next_st, act_cost in get_successors(current):
            if next_st not in visited:
                visited.add(next_st)
                parent[next_st] = (current, act, act_cost)
                queue.append(next_st)

    return SearchResult("BFS", None, None, None, nodes_expanded, time.time() - t0)


# ==========================================
# 2. Depth-First Search (DFS)
# ==========================================
def dfs(initial_state: State, max_depth: int = 50) -> SearchResult:
    """
    Depth-First Search (Graph Search):
    Explores deep into search tree using a LIFO stack.
    Uses visited set to avoid cycles and redundant state expansions.
    """
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


# ==========================================
# 3. Iterative Deepening Search (IDS)
# ==========================================
def ids(initial_state: State, max_depth: int = 30) -> SearchResult:
    """
    Iterative Deepening Search:
    Repeatedly applies depth-limited search with increasing depth bounds.
    Guarantees step-optimality while retaining linear space complexity.
    """
    t0 = time.time()
    total_nodes = 0

    def dls(state: State, limit: int, path: list, visited: set):
        nonlocal total_nodes
        total_nodes += 1

        if state.is_goal():
            return True, path

        if limit <= 0:
            return False, None

        for act, next_st, act_cost in get_successors(state):
            if next_st in visited:
                continue
            visited.add(next_st)
            path.append((act, act_cost, next_st))
            found, sol = dls(next_st, limit - 1, path, visited)
            if found:
                return True, sol
            path.pop()
            visited.remove(next_st)

        return False, None

    for depth in range(max_depth + 1):
        visited_set = {initial_state}
        found, sol_path = dls(initial_state, depth, [], visited_set)
        if found:
            total_cost = sum(c for _, c, _ in sol_path)
            return SearchResult("IDS", total_cost, len(sol_path), sol_path, total_nodes, time.time() - t0)

    return SearchResult("IDS", None, None, None, total_nodes, time.time() - t0)


# ==========================================
# 4. Uniform-Cost Search (UCS / Dijkstra)
# ==========================================
def ucs(initial_state: State) -> SearchResult:
    """
    Uniform-Cost Search:
    Expands the node with the lowest path cost g(n).
    Guarantees cost-optimality for positive edge weights.
    """
    t0 = time.time()
    counter = 0
    pq = [(0.0, counter, initial_state)]
    visited = {initial_state: 0.0}
    parent = {}
    nodes_expanded = 0

    while pq:
        cost, _, current = heapq.heappop(pq)
        nodes_expanded += 1

        if current.is_goal():
            path = []
            curr = current
            while curr in parent:
                prev_st, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                curr = prev_st
            path.reverse()
            return SearchResult("UCS", cost, len(path), path, nodes_expanded, time.time() - t0)

        if cost > visited.get(current, float('inf')):
            continue

        for act, next_st, act_cost in get_successors(current):
            new_cost = cost + act_cost
            if next_st not in visited or new_cost < visited[next_st]:
                visited[next_st] = new_cost
                parent[next_st] = (current, act, act_cost)
                counter += 1
                heapq.heappush(pq, (new_cost, counter, next_st))

    return SearchResult("UCS", None, None, None, nodes_expanded, time.time() - t0)


# ==========================================
# 5. Custom Greedy Column Search
# ==========================================
def greedy_column_search(initial_state: State) -> SearchResult:
    """
    Custom Greedy Algorithm:
    Empties each column separately top-to-bottom without opening any side gates.
    Matches the exact greedy behavior specified by the professor.
    """
    t0 = time.time()
    R = initial_state.rows
    path = []
    total_cost = 0.0
    curr_state = initial_state
    nodes_expanded = 0

    # Helper to empty a single column
    def empty_col(col_idx: int, state: State):
        nonlocal total_cost, nodes_expanded
        col_sand = state.col0 if col_idx == 0 else state.col1
        col_gates = state.gates0 if col_idx == 0 else state.gates1

        while sum(col_sand) > 0.0 or any(col_gates):
            for r in range(R):
                # Check if gate r can flush sand
                if r < R - 1:
                    top_r = r
                    while top_r > 0 and col_gates[top_r - 1]:
                        top_r -= 1
                    if sum(col_sand[i] for i in range(top_r, r + 1)) == 0.0:
                        continue
                else:
                    top_r = R - 1
                    while top_r > 0 and col_gates[top_r - 1]:
                        top_r -= 1
                    if sum(col_sand[i] for i in range(top_r, R)) == 0.0:
                        continue

                new_sand, new_gates, act_cost = open_vertical_gate(col_sand, col_gates, r)
                total_cost += act_cost
                nodes_expanded += 1
                act = Action('vertical', col_idx, r, f"Flush col {col_idx} gate {r}")

                if col_idx == 0:
                    state = State(new_sand, state.col1, new_gates, state.gates1)
                else:
                    state = State(state.col0, new_sand, state.gates0, new_gates)
                path.append((act, act_cost, state))
                col_sand = new_sand
                col_gates = new_gates

        return state

    curr_state = empty_col(0, curr_state)
    curr_state = empty_col(1, curr_state)

    return SearchResult("Greedy", total_cost, len(path), path, nodes_expanded, time.time() - t0)


# ==========================================
# 6. A* Search
# ==========================================
def astar(initial_state: State, heuristic: Callable[[State], float] = h_gravity) -> SearchResult:
    """
    A* Search:
    Best-first search using f(n) = g(n) + h(n).
    Guarantees cost-optimality with admissible and consistent heuristics.
    """
    t0 = time.time()
    counter = 0
    h0 = heuristic(initial_state)
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
                prev_st, act, act_cost = parent[curr]
                path.append((act, act_cost, curr))
                curr = prev_st
            path.reverse()
            return SearchResult("A*", g, len(path), path, nodes_expanded, time.time() - t0)

        if g > visited.get(current, float('inf')):
            continue

        for act, next_st, act_cost in get_successors(current):
            new_g = g + act_cost
            if next_st not in visited or new_g < visited[next_st]:
                visited[next_st] = new_g
                parent[next_st] = (current, act, act_cost)
                counter += 1
                new_f = new_g + heuristic(next_st)
                heapq.heappush(pq, (new_f, new_g, counter, next_st))

    return SearchResult("A*", None, None, None, nodes_expanded, time.time() - t0)


# ==========================================
# 7. Recursive Best-First Search (RBFS)
# ==========================================
class _RBFSNode:
    __slots__ = ('state', 'parent', 'action', 'cost', 'g', 'h', 'f')
    def __init__(self, state, parent=None, action=None, cost=0.0, g=0.0, h=0.0, f=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.g = g
        self.h = h
        self.f = f

def rbfs(initial_state: State, heuristic: Callable[[State], float] = h_gravity, max_nodes: int = 200000) -> SearchResult:
    """
    Recursive Best-First Search:
    Linear space best-first heuristic search (Russell & Norvig AIMA 4th ed).
    Tracks an f-limit and updates backup values.
    """
    t0 = time.time()
    nodes_expanded = 0

    def _rbfs(node: _RBFSNode, f_limit: float):
        nonlocal nodes_expanded
        nodes_expanded += 1

        if nodes_expanded > max_nodes:
            return None, float('inf')

        if node.state.is_goal():
            return node, 0.0

        successors = []
        # Ancestor check to avoid cycles along the current branch
        ancestor = node.parent
        ancestor_states = set()
        while ancestor:
            ancestor_states.add(ancestor.state)
            ancestor = ancestor.parent

        for act, next_st, act_cost in get_successors(node.state):
            if next_st in ancestor_states:
                continue
            g = node.g + act_cost
            h = heuristic(next_st)
            f = max(g + h, node.f)
            child = _RBFSNode(next_st, parent=node, action=act, cost=act_cost, g=g, h=h, f=f)
            successors.append(child)

        if not successors:
            return None, float('inf')

        while True:
            successors.sort(key=lambda x: x.f)
            best = successors[0]
            if best.f > f_limit:
                return None, best.f

            alternative = successors[1].f if len(successors) > 1 else float('inf')
            result, best.f = _rbfs(best, min(f_limit, alternative))
            if result is not None:
                return result, best.f

    h0 = heuristic(initial_state)
    root = _RBFSNode(initial_state, g=0.0, h=h0, f=h0)
    result_node, _ = _rbfs(root, float('inf'))

    if result_node:
        path = []
        curr = result_node
        while curr.parent:
            path.append((curr.action, curr.cost, curr.state))
            curr = curr.parent
        path.reverse()
        return SearchResult("RBFS", result_node.g, len(path), path, nodes_expanded, time.time() - t0)

    return SearchResult("RBFS", None, None, None, nodes_expanded, time.time() - t0)
