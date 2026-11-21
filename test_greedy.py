from test_gravity import ColumnState, open_vertical_gate

def greedy_empty_column(sand_initial):
    """
    Simulate greedy column emptying.
    Scans from top to bottom opening gates where sand is present,
    until the column is completely empty (all sand == 0).
    """
    R = len(sand_initial)
    c = ColumnState(sand_initial)
    total_cost = 0.0
    action_log = []

    # While there is sand in the column
    while any(s > 0 for s in c.sand):
        # We sweep from top to bottom
        # Find highest row with sand
        for r in range(R):
            # If gate r can move sand down or drain out:
            # specifically, if there is sand in row r (or jammed above it),
            # or if r == R-1 and c.sand[R-1] > 0
            if c.sand[r] > 0:
                c, cost = open_vertical_gate(c, r)
                total_cost += cost
                action_log.append((r, cost, list(c.sand), list(c.open_gates)))
    return total_cost, action_log

print("Testing greedy on teacher's 4-row cols:")
cost0, log0 = greedy_empty_column([1.0, 0.0, 0.0, 1.0])
print("Col 0:", cost0, [x[1] for x in log0])

cost1, log1 = greedy_empty_column([0.0, 1.0, 1.0, 0.0])
print("Col 1:", cost1, [x[1] for x in log1])
print("Total greedy:", cost0 + cost1)
