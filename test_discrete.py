import heapq
import time
from sand_drawer import State, Action, open_vertical_gate

def get_successors_discrete(state: State):
    R = len(state.col0)
    successors = []

    # 1. Vertical gate actions for Column 0
    for g in range(R):
        if g < R - 1 and state.gates0[g]:
            continue
        if g < R - 1:
            top_r = g
            while top_r > 0 and state.gates0[top_r - 1]:
                top_r -= 1
            if sum(state.col0[i] for i in range(top_r, g + 1)) == 0.0:
                continue
        else:
            # Bottom gate
            # Can be opened if row R-1 has sand OR any row connected via open gates has sand
            top_r = R - 1
            while top_r > 0 and state.gates0[top_r - 1]:
                top_r -= 1
            if sum(state.col0[i] for i in range(top_r, R)) == 0.0:
                continue

        new_sand, new_gates, cost = open_vertical_gate(state.col0, state.gates0, g)
        act = Action('vertical', 0, g, f"Flush col 0 gate {g}")
        next_state = State(new_sand, state.col1, new_gates, state.gates1)
        successors.append((act, next_state, cost))

    # 2. Vertical gate actions for Column 1
    for g in range(R):
        if g < R - 1 and state.gates1[g]:
            continue
        if g < R - 1:
            top_r = g
            while top_r > 0 and state.gates1[top_r - 1]:
                top_r -= 1
            if sum(state.col1[i] for i in range(top_r, g + 1)) == 0.0:
                continue
        else:
            top_r = R - 1
            while top_r > 0 and state.gates1[top_r - 1]:
                top_r -= 1
            if sum(state.col1[i] for i in range(top_r, R)) == 0.0:
                continue

        new_sand, new_gates, cost = open_vertical_gate(state.col1, state.gates1, g)
        act = Action('vertical', 1, g, f"Flush col 1 gate {g}")
        next_state = State(state.col0, new_sand, state.gates0, new_gates)
        successors.append((act, next_state, cost))

    # 3. Side gate actions: ONLY when one cell is 1.0 and the other is 0.0
    # (so both become 0.5, preserving discrete states in {0, 0.5, 1})
    for r in range(R):
        c0, c1 = state.col0[r], state.col1[r]
        if (c0 == 1.0 and c1 == 0.0) or (c0 == 0.0 and c1 == 1.0):
            new_c0 = list(state.col0)
            new_c1 = list(state.col1)
            new_c0[r] = 0.5
            new_c1[r] = 0.5
            next_state = State(tuple(new_c0), tuple(new_c1), state.gates0, state.gates1)
            act = Action('side', None, r, f"Side gate row {r}")
            successors.append((act, next_state, 1.0))

    return successors

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

        for act, next_st, act_cost in get_successors_discrete(current):
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
print("Actions:")
for act, c, st in path:
    print(f"  {act.description} (cost={c})")
