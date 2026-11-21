import random
from test_improved_astar import improved_h, solve_astar_fast
from test_discrete import State, solve_ucs

print("Verifying improved_h admissibility...")
random.seed(999)
all_ok = True
for i in range(50):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))

    ucs_cost, _, _ = solve_ucs(st)
    h_val = improved_h(st)
    if h_val > ucs_cost:
        print(f"FAILED on state {i}! h={h_val} > ucs={ucs_cost}")
        all_ok = False
        break

if all_ok:
    print("ALL 50 states PASSED! improved_h is strictly admissible!")
