from sand_drawer import State, get_successors

init_state = State(
    col0=(1.0, 0.0, 0.0, 1.0),
    col1=(0.0, 1.0, 1.0, 0.0),
    gates0=(False, False, False),
    gates1=(False, False, False)
)

print("Initial:")
print(init_state)
succs = get_successors(init_state)
print(f"Successors count: {len(succs)}")
for act, nxt, cost in succs:
    print(f"{act.description} (cost={cost})")
