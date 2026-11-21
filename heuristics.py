"""
heuristics.py
=============
Heuristic functions for Informed Search (A* and RBFS).

Heuristics implemented:
1. h0 (Trivial Heuristic):
   h(n) = 0.0 for all n.
   Guaranteed admissible and consistent (reduces A* to UCS).

2. h_gravity (Vertical Gravity & Gate Bound):
   For each column with sand:
   - A bottom exit flush is required: adds at least 3.0 (since min sand flushed is 0.5, cost >= 1 + 4*0.5 = 3.0).
   - Any sand residing above a closed gate r must pass through gate r, requiring at least one flush (cost >= 1.0).
   Proven admissible (h(n) <= h*(n)) and consistent (h(n) <= c(n, a, n') + h(n')).

3. h_exit_bound (Exit Bound):
   Based on total sand remaining.
"""

from environment import State

def h0(state: State) -> float:
    """Trivial heuristic: 0.0."""
    return 0.0


def h_gravity(state: State) -> float:
    """
    Vertical Gravity Gate Bound Heuristic.
    
    Mathematical proof of admissibility:
    1. If state is goal, cost = 0, h(goal) = 0.
    2. If column c has any sand (sum(col) > 0):
       Every particle of sand must eventually leave the drawer via the bottom gate.
       When the bottom gate opens with sand, the upper box has s >= 0.5.
       The cost of this exit action is 1 + 4*(s + 0) >= 1 + 4*(0.5) = 3.0.
    3. For any row r < R - 1 where sand exists at or above row r, and gate r is currently closed:
       Gravity pulls sand strictly downwards. The sand cannot bypass gate r to reach the exit.
       Opening gate r incurs a non-negative cost of 1 + 4*(s + s') >= 1.0.
    4. Since these gate openings and exit flushes are disjoint, necessary operations,
       their sum provides a rigorous lower bound on any valid solution path:
       h_gravity(state) <= h*(state).
    """
    if state.is_goal():
        return 0.0

    R = state.rows
    h = 0.0

    for col, gates in [(state.col0, state.gates0), (state.col1, state.gates1)]:
        if sum(col) == 0.0:
            continue
        # Base exit flush
        col_h = 3.0
        # Closed gates below sand
        for r in range(R - 1):
            if sum(col[:r + 1]) > 0.0 and not gates[r]:
                col_h += 1.0
        h += col_h

    return h


def h_exit_bound(state: State) -> float:
    """
    Lower bound based on total sand exiting.
    """
    total = state.total_sand()
    if total == 0.0:
        return 0.0
    # At least one bottom flush per column with sand
    cols_with_sand = (1 if sum(state.col0) > 0 else 0) + (1 if sum(state.col1) > 0 else 0)
    return cols_with_sand * 3.0


def get_heuristic(name: str):
    name = name.lower().strip()
    if name in ('h0', 'zero', 'trivial'):
        return h0
    elif name in ('h_gravity', 'gravity', 'default'):
        return h_gravity
    elif name in ('h_exit', 'exit'):
        return h_exit_bound
    else:
        raise ValueError(f"Unknown heuristic name: {name}")
