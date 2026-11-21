import heapq
from sand_drawer import open_vertical_gate

# Precompute single column optimal costs for all possible (sand, gates)
# sand is a 5-tuple in {0.0, 0.5, 1.0}^5 (243 tuples)
# gates is a 4-tuple of bools (16 tuples)
# Total states = 3888

# Goal is sand = (0,0,0,0,0), gates = (False, False, False, False)
# We can run standard Dijkstra / UCS for each of the 243 initial closed-gate sand states!

def solve_col(sand):
    # Initial state
    init_gates = (False, False, False, False)
    pq = [(0.0, sand, init_gates, 0)] # (cost, sand, gates, actions)
    dist = {(sand, init_gates): 0.0}
    actions_count = {(sand, init_gates): 0}

    while pq:
        cost, s, g, n_act = heapq.heappop(pq)
        if sum(s) == 0.0 and not any(g):
            return cost, n_act

        if cost > dist.get((s, g), float('inf')):
            continue

        R = len(s)
        for gate_idx in range(R):
            if gate_idx < R - 1 and g[gate_idx]:
                continue
            if gate_idx < R - 1:
                top_r = gate_idx
                while top_r > 0 and g[top_r - 1]:
                    top_r -= 1
                if sum(s[i] for i in range(top_r, gate_idx + 1)) == 0.0:
                    continue
            else:
                top_r = R - 1
                while top_r > 0 and g[top_r - 1]:
                    top_r -= 1
                if sum(s[i] for i in range(top_r, R)) == 0.0:
                    continue

            new_sand, new_gates, act_cost = open_vertical_gate(s, g, gate_idx)
            new_cost = cost + act_cost
            next_key = (new_sand, new_gates)
            if next_key not in dist or new_cost < dist[next_key]:
                dist[next_key] = new_cost
                actions_count[next_key] = n_act + 1
                heapq.heappush(pq, (new_cost, new_sand, new_gates, n_act + 1))

    return 0.0, 0

print("Testing single col solver...")
print("col [1,0,0,1,0]:", solve_col((1.0, 0.0, 0.0, 1.0, 0.0)))
