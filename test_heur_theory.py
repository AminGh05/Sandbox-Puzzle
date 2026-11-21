import random
from test_discrete import State, solve_ucs, get_successors_discrete

def random_state_5x2(seed=None):
    if seed is not None:
        random.seed(seed)
    choices = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(choices, weights=weights, k=5))
    c1 = tuple(random.choices(choices, weights=weights, k=5))
    g0 = (False, False, False, False)
    g1 = (False, False, False, False)
    return State(c0, c1, g0, g1)

# Let's test candidate heuristics
def h_sand_exit(state: State) -> float:
    # Every unit of sand must exit bottom gate.
    # Bottom exit flush with sand s has cost 1 + 4*s.
    # Total sand M = sum(c0) + sum(c1).
    # If M == 0: return 0.
    # At least 4*M + ceil(M) or 4*M + 1?
    # Wait, can 2 units of sand exit in a SINGLE bottom flush?
    # If gate 3 is open and row 3 has 1, and row 4 has 1:
    # When bottom gate opens: row 4 exits, and row 3 exits through open gate 3!
    # Upper box is row 4 (s=1, s'=0 -> cost = 1 + 4*(1+0) = 5).
    # But row 3 ALSO drained! That drained 2 units for cost 5!
    # Wait, 4*M would be 4 * 2 = 8 > 5!
    # So 4*M is NOT admissible if sand can drain through open gates!
    pass
