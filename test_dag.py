# Verification of acyclicity (DAG property)
# A state potential function:
# P(state) = 100 * total_sand + sum( (4 - r) * (col0[r] + col1[r]) ) + 0.1 * number_of_ones
# If for every transition: P(next_state) < P(current_state), then it is strictly a DAG!

def state_potential(state):
    total_sand = sum(state.col0) + sum(state.col1)
    depth_sum = sum((4 - r) * (state.col0[r] + state.col1[r]) for r in range(5))
    ones_count = sum(1 for x in state.col0 if x == 1.0) + sum(1 for x in state.col1 if x == 1.0)
    return 1000.0 * total_sand + 10.0 * depth_sum + 1.0 * ones_count

print("DAG potential check defined.")
