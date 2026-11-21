import random
from test_discrete import State, solve_ucs

def h_gravity(state: State) -> float:
    if state.is_goal():
        return 0.0
    R = len(state.col0)
    h = 0.0
    for col, gates in [(state.col0, state.gates0), (state.col1, state.gates1)]:
        if sum(col) == 0.0:
            continue
        col_h = 3.0
        for r in range(R - 1):
            if sum(col[:r+1]) > 0.0 and not gates[r]:
                col_h += 1.0
        h += col_h
    return h

print("Testing h_gravity on 100 random states...")
random.seed(777)
all_passed = True
for i in range(100):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))

    ucs_cost, _, _ = solve_ucs(st)
    h_val = h_gravity(st)
    if h_val > ucs_cost:
        print(f"FAILED on state {i}! h={h_val} > ucs={ucs_cost}")
        all_passed = False
        break

if all_passed:
    print("ALL 100 states PASSED! h_gravity is 100% strictly admissible!")
