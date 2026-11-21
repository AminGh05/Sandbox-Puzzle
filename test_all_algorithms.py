from environment import create_teacher_state, create_random_state
from search_algorithms import bfs, dfs, ids, ucs, greedy_column_search, astar, rbfs

print("=" * 60)
print("TESTING ALL 7 ALGORITHMS ON TEACHER 4x2 STATE")
print("=" * 60)

teacher_state = create_teacher_state()
print(teacher_state)
print()

for solver in [greedy_column_search, bfs, ucs, astar, ids, dfs]:
    res = solver(teacher_state)
    print(f"[{res.algorithm:6s}] Cost: {res.cost:5.1f} | Steps: {res.steps:2d} | Nodes: {res.nodes_expanded:6d} | Time: {res.elapsed_time*1000:6.1f} ms")

print("\nRunning RBFS (small test)...")
res_rbfs = rbfs(teacher_state, max_nodes=50000)
if res_rbfs.cost is not None:
    print(f"[{res_rbfs.algorithm:6s}] Cost: {res_rbfs.cost:5.1f} | Steps: {res_rbfs.steps:2d} | Nodes: {res_rbfs.nodes_expanded:6d} | Time: {res_rbfs.elapsed_time*1000:6.1f} ms")
else:
    print(f"[RBFS  ] Node limit reached ({res_rbfs.nodes_expanded} nodes)")

print("\n" + "=" * 60)
print("TESTING ON RANDOM 5x2 STATE")
print("=" * 60)
rnd_state = create_random_state(rows=5, seed=42)
print(rnd_state)
print()

for solver in [greedy_column_search, bfs, ucs, astar]:
    res = solver(rnd_state)
    print(f"[{res.algorithm:6s}] Cost: {res.cost:5.1f} | Steps: {res.steps:2d} | Nodes: {res.nodes_expanded:6d} | Time: {res.elapsed_time*1000:6.1f} ms")
