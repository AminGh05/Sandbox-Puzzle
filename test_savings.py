import itertools
import random
from test_col_solver import solve_col
from test_discrete import State, solve_ucs

# Precompute 243
values = [0.0, 0.5, 1.0]
all_cols = list(itertools.product(values, repeat=5))
col_cache = {c: solve_col(c) for c in all_cols}

random.seed(42)
max_saving = 0.0
savings = []

for i in range(100):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    
    ucs_cost, path, _ = solve_ucs(st)
    independent_cost = col_cache[c0][0] + col_cache[c1][0]
    saving = independent_cost - ucs_cost
    savings.append(saving)
    if saving > max_saving:
        max_saving = saving

print(f"Max saving observed across 100 random states: {max_saving}")
print(f"Average saving: {sum(savings)/len(savings):.2f}")
print(f"Min saving: {min(savings)}")
