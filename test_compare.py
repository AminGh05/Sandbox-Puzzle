import itertools
import random
import time
from test_discrete import State, solve_ucs
from test_col_solver import solve_col

# Precompute 243
values = [0.0, 0.5, 1.0]
all_cols = list(itertools.product(values, repeat=5))
col_cache = {c: solve_col(c) for c in all_cols}

def fast_solve_state(c0, c1):
    # Find all rows where side gate is possible: {c0[r], c1[r]} == {0.0, 1.0}
    eligible_rows = [r for r in range(5) if {c0[r], c1[r]} == {0.0, 1.0}]
    
    best_cost = col_cache[c0][0] + col_cache[c1][0]
    best_act = col_cache[c0][1] + col_cache[c1][1]
    best_b = 0

    # Test all subsets of eligible rows
    num_subsets = 1 << len(eligible_rows)
    for mask in range(1, num_subsets):
        k = 0
        new_c0 = list(c0)
        new_c1 = list(c1)
        for i, r in enumerate(eligible_rows):
            if (mask >> i) & 1:
                k += 1
                new_c0[r] = 0.5
                new_c1[r] = 0.5
        t_c0 = tuple(new_c0)
        t_c1 = tuple(new_c1)
        cost = k * 1.0 + col_cache[t_c0][0] + col_cache[t_c1][0]
        act = k + col_cache[t_c0][1] + col_cache[t_c1][1]
        if cost < best_cost:
            best_cost = cost
            best_act = act
            best_b = k
        elif cost == best_cost and act < best_act:
            best_act = act
            best_b = k

    return best_cost, best_act, best_b

# Compare with full UCS on 20 states
print("Comparing fast_solve_state vs full UCS...")
random.seed(42)
matches = 0
for i in range(20):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    ucs_cost, path, _ = solve_ucs(st)
    fast_cost, fast_act, fast_b = fast_solve_state(c0, c1)
    
    print(f"State {i}: UCS cost = {ucs_cost}, Fast cost = {fast_cost}")
    if ucs_cost == fast_cost:
        matches += 1
    else:
        print(f"  MISMATCH on state {i}! UCS={ucs_cost}, Fast={fast_cost}")

print(f"\nResult: {matches} / 20 matched!")
