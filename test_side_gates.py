from test_gravity import ColumnState, open_vertical_gate

print("--- Side Gates Approach ---")
# Col 0 after side gates at row 1 and row 2: [1.0, 0.5, 0.5, 1.0]
c0 = ColumnState([1.0, 0.5, 0.5, 1.0])
costs0 = []
for g in [0, 1, 2, 3]:
    c0, cost = open_vertical_gate(c0, g)
    costs0.append(cost)
    print(f"Col 0: open gate {g} -> cost={cost}, state={c0}")
print(f"Col 0 sum: {costs0} = {sum(costs0)}")

# Col 1 after side gates at row 1 and row 2: [0.0, 0.5, 0.5, 0.0]
c1 = ColumnState([0.0, 0.5, 0.5, 0.0])
costs1 = []
for g in [1, 2, 3]:
    c1, cost = open_vertical_gate(c1, g)
    costs1.append(cost)
    print(f"Col 1: open gate {g} -> cost={cost}, state={c1}")
print(f"Col 1 sum: {costs1} = {sum(costs1)}")

print(f"Total side gates approach cost: 1+1 + {sum(costs0)} + {sum(costs1)} = {2 + sum(costs0) + sum(costs1)}")

print("\n--- Other alternative ---")
# Col 0 opened in order [1, 0, 2, 3]:
# wait, teacher's trace: 3 + 5 + 9 + 9 + 5 = 31!
# Let's test what order gives [3, 5, 9, 9, 5]
c0_alt = ColumnState([1.0, 0.5, 0.5, 1.0])
costs_alt = []
for g in [1, 0, 1, 2, 3]:
    c0_alt, cost = open_vertical_gate(c0_alt, g)
    costs_alt.append(cost)
    print(f"Col 0 alt: open gate {g} -> cost={cost}, state={c0_alt}")
print(f"Col 0 alt sum: {costs_alt} = {sum(costs_alt)}")
