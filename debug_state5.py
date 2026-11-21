import random
from test_discrete import State, solve_ucs
from test_col_solver import solve_col

random.seed(999)
for i in range(6):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    if i == 5:
        st = State(c0, c1, (False, False, False, False), (False, False, False, False))
        print("State 5:")
        print(st)
        cost, path, _ = solve_ucs(st)
        print("UCS cost:", cost)
        for act, c, s in path:
            print(" ", act.description, f"(cost={c})")
        c0_cost = solve_col(c0)[0]
        c1_cost = solve_col(c1)[0]
        print(f"Independent costs: c0={c0_cost}, c1={c1_cost}, sum={c0_cost + c1_cost}")
        print("Difference:", (c0_cost + c1_cost) - cost)
