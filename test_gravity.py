# Complete physics simulation test

class ColumnState:
    def __init__(self, sand, open_gates=None):
        # sand is a list of floats, e.g. [1.0, 0.0, 0.0, 1.0]
        # open_gates is a list of booleans of length len(sand) - 1
        self.sand = list(sand)
        self.open_gates = list(open_gates) if open_gates is not None else [False] * (len(sand) - 1)

    def copy(self):
        return ColumnState(self.sand, self.open_gates)

    def __repr__(self):
        return f"sand={self.sand}, gates={self.open_gates}"

def open_vertical_gate(col: ColumnState, gate_idx: int):
    """
    gate_idx:
      0 .. R-2: gate between row gate_idx and row gate_idx + 1
      R-1: bottom gate (out of the drawer)
    Returns: (new_col_state, cost)
    """
    R = len(col.sand)
    new_sand = list(col.sand)
    new_gates = list(col.open_gates)

    s_before = new_sand[gate_idx]

    if gate_idx == R - 1:
        # Bottom gate opens!
        # Sand in row R-1 drains out.
        # Furthermore, any rows above R-1 connected by currently open gates also drain down!
        # Let's see: find connected component of open gates above R-1.
        # If gate R-2 is open, row R-2 drains too, and if R-3 is open, row R-3 drains, etc.
        r = R - 1
        new_sand[r] = 0.0
        while r > 0 and new_gates[r - 1]:
            new_sand[r - 1] = 0.0
            new_gates[r - 1] = False # unjams because no sand left
            r -= 1
        
        s_after = new_sand[gate_idx] # which is 0.0
        cost = 1 + 4 * (s_before + s_after)
        return ColumnState(new_sand, new_gates), cost

    else:
        # Gate between r and r+1
        r = gate_idx
        # This gate is opened:
        new_gates[r] = True

        # Now sand flows through all open gates in the connected component containing r and r+1!
        # Let's find the connected component of open gates:
        # Start from highest row connected to r via open gates
        top_r = r
        while top_r > 0 and new_gates[top_r - 1]:
            top_r -= 1

        # Lowest row connected to r+1:
        bot_r = r + 1
        while bot_r < R - 1 and new_gates[bot_r]:
            bot_r += 1

        # Total sand in rows top_r .. bot_r:
        total_sand = sum(new_sand[i] for i in range(top_r, bot_r + 1))

        # Gravity settles sand to the lowest possible rows (capacity 1.0 per row):
        rem = total_sand
        for i in range(bot_r, top_r - 1, -1):
            amount = min(1.0, rem)
            new_sand[i] = amount
            rem -= amount

        # Now check which gates can close!
        # "unless the plank under the lower one gets opened and some of the sand moves,
        #  so the sand between the first mentioned cells gets less than 1 unit."
        # A gate k between k and k+1 can close if the upper cell k is empty (sand <= 0),
        # meaning no sand is trapped between k and k+1.
        for k in range(top_r, bot_r):
            if new_sand[k] == 0:
                new_gates[k] = False
            else:
                # Sand still in cell k and cell k+1 is full, so gate k remains jammed open
                new_gates[k] = True

        s_after = new_sand[r]
        cost = 1 + 4 * (s_before + s_after)
        return ColumnState(new_sand, new_gates), cost


# Test Col 0 of Greedy: [1, 0, 0, 1]
c = ColumnState([1.0, 0.0, 0.0, 1.0])
print("Initial Col 0:", c)
costs = []
for g in [0, 1, 2, 3]:
    c, cost = open_vertical_gate(c, g)
    costs.append(cost)
    print(f"Open gate {g} -> cost={cost}, state={c}")
print(f"Col 0 total cost: {costs} sum={sum(costs)}")

# Test Col 1 of Greedy: [0, 1, 1, 0]
c = ColumnState([0.0, 1.0, 1.0, 0.0])
print("\nInitial Col 1:", c)
costs = []
for g in [1, 2, 3]:
    c, cost = open_vertical_gate(c, g)
    costs.append(cost)
    print(f"Open gate {g} -> cost={cost}, state={c}")
print(f"Col 1 total cost: {costs} sum={sum(costs)}")
