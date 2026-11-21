import random
from test_discrete import State, solve_ucs, get_successors_discrete

# Test on 100 random states:
# Does any optimal path have a side gate AFTER a vertical flush?
random.seed(42)
side_after_vertical = 0
total_tested = 100

for i in range(total_tested):
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    st = State(c0, c1, (False, False, False, False), (False, False, False, False))
    
    cost, path, _ = solve_ucs(st)
    if path:
        saw_vertical = False
        for act, c, s in path:
            if act.type == 'vertical':
                saw_vertical = True
            elif act.type == 'side' and saw_vertical:
                side_after_vertical += 1
                print(f"State {i}: Found side gate AFTER vertical flush!")
                break

print(f"Total states where side gate was used after vertical flush: {side_after_vertical} / {total_tested}")
