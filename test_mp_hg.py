import multiprocessing as mp
import time
import itertools
from environment import State, get_successors
from heuristics import h_gravity

def solve_pair_hg(pair):
    c0, c1 = pair
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    if st.is_goal():
        return (c0, c1, 0.0, 0, 0)

    import heapq
    counter = 0
    h0 = h_gravity(st)
    pq = [(h0, 0.0, counter, st)]
    visited = {st: 0.0}
    parent = {}

    while pq:
        f, g, _, curr = heapq.heappop(pq)
        if curr.is_goal():
            path = []
            c_node = curr
            while c_node in parent:
                prev_st, act, act_c = parent[c_node]
                path.append(act)
                c_node = prev_st
            num_actions = len(path)
            num_b = sum(1 for act in path if act.type == 'side')
            return (c0, c1, g, num_actions, num_b)

        if g > visited.get(curr, float('inf')):
            continue

        for act, next_st, act_cost in get_successors(curr):
            new_g = g + act_cost
            if next_st not in visited or new_g < visited[next_st]:
                visited[next_st] = new_g
                parent[next_st] = (curr, act, act_cost)
                counter += 1
                heapq.heappush(pq, (new_g + h_gravity(next_st), new_g, counter, next_st))

    return (c0, c1, 0.0, 0, 0)

if __name__ == '__main__':
    values = [0.0, 0.5, 1.0]
    all_cols = list(itertools.product(values, repeat=5))
    pairs = []
    for i in range(len(all_cols)):
        for j in range(i, len(all_cols)):
            pairs.append((all_cols[i], all_cols[j]))
            if len(pairs) >= 200:
                break
        if len(pairs) >= 200:
            break

    print(f"Testing 200 pairs with h_gravity on {mp.cpu_count()} cores...")
    t0 = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(solve_pair_hg, pairs)
    dt = time.time() - t0
    print(f"Solved 200 pairs in {dt:.2f} seconds ({len(results)/dt:.1f} pairs/sec)!")
