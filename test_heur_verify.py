import random
from test_discrete import State, solve_ucs, get_successors_discrete

def compute_h(state: State) -> float:
    if state.is_goal():
        return 0.0

    R = len(state.col0)
    h = 0.0

    # For each column:
    for col_idx, (col, gates) in enumerate([(state.col0, state.gates0), (state.col1, state.gates1)]):
        total_sand_col = sum(col)
        if total_sand_col == 0.0:
            continue

        # If there is sand, at least one bottom flush must occur.
        # Cost of bottom flush with sand: at least 3.0 (if sand=0.5) or 5.0 (if sand=1.0).
        # We can conservatively take 3.0.
        col_h = 3.0

        # Also, consider the highest row that has sand:
        # If sand is at row r < R-1, and gates between r and R-1 are closed,
        # each closed gate between the sand and the bottom that must open adds at least 1.0!
        # Let's count how many closed gates are below the highest sand row:
        for r in range(R - 1):
            # If any sand at or above row r, and gate r is closed:
            # sand above gate r must pass through gate r, which costs at least 1.0 (actually at least 3.0).
            if sum(col[:r+1]) > 0 and not gates[r]:
                col_h += 1.0

        h += col_h

    return h

# Let's verify compute_h on 50 random states
random.seed(123)
passed = True
for i in range(50):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    
    true_cost, path, _ = solve_ucs(st)
    h_val = compute_h(st)
    if h_val > true_cost:
        print(f"FAILED on state {i}: h={h_val} > true_cost={true_cost}")
        passed = False
        break

if passed:
    print("ALL 50 random states PASSED admissibility test! compute_h <= true_cost")
