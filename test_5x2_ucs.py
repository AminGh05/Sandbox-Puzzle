import random
import time
from test_discrete import State, solve_ucs

# Generate a random 5x2 state according to the problem probabilities:
# 0.5 chance empty (0.0), 0.3 chance full (1.0), 0.2 chance half-full (0.5)

def random_state_5x2(seed=None):
    if seed is not None:
        random.seed(seed)
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    g0 = (False, False, False, False)
    g1 = (False, False, False, False)
    return State(c0, c1, g0, g1)

st = random_state_5x2(42)
print("Initial 5x2 state:")
print(st)
t0 = time.time()
cost, path, nodes = solve_ucs(st)
dt = time.time() - t0
print(f"Optimal cost: {cost} in {dt:.3f}s (expanded {nodes} nodes)")
for act, c, s in path:
    print(f"  {act.description} (cost={c})")
