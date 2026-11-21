"""
environment.py
==============
Formal state and transition model for the Sand Drawer Puzzle.

Environment:
- Grid of R rows and 2 columns (default R=5, columns=2).
- Cell capacities: 1.0 unit of sand.
- Discrete sand values: 0.0 (empty), 0.5 (half-full), 1.0 (full).
- Initial seeding probabilities: 0.5 for empty, 0.3 for full, 0.2 for half-full.

Actions:
- Action a (Top-down gate):
  Flushes sand from upper row r to row r+1 (or out of the drawer for the bottom row).
  Cost: 1 + 4 * (s + s')
  where s is the state of the upper box before flushing, and s' is after flushing.
  If lower cell cannot hold all sand (u + d > 1.0), the gate remains jammed open
  until lower gates drain the sand.
- Action b (Side gate):
  Equalizes sand between col 0 and col 1 at row r: (c0 + c1) / 2.
  Cost: 1.0.
"""

from typing import Tuple, List, Optional, NamedTuple
import random

class Action(NamedTuple):
    type: str          # 'vertical' or 'side'
    col: Optional[int] # 0 or 1 for vertical, None for side
    index: int         # gate index (0..R-1) or row index (0..R-1)
    description: str

class State:
    __slots__ = ('col0', 'col1', 'gates0', 'gates1', '_hash')

    def __init__(self, col0: Tuple[float, ...], col1: Tuple[float, ...],
                 gates0: Tuple[bool, ...], gates1: Tuple[bool, ...]):
        self.col0 = col0
        self.col1 = col1
        self.gates0 = gates0
        self.gates1 = gates1
        self._hash = hash((col0, col1, gates0, gates1))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.col0 == other.col0 and
                self.col1 == other.col1 and
                self.gates0 == other.gates0 and
                self.gates1 == other.gates1)

    def is_goal(self) -> bool:
        """Goal: all sand is drained and all gates are closed."""
        return (not any(self.col0) and not any(self.col1) and
                not any(self.gates0) and not any(self.gates1))

    def total_sand(self) -> float:
        return sum(self.col0) + sum(self.col1)

    @property
    def rows(self) -> int:
        return len(self.col0)

    def to_grid(self) -> List[List[float]]:
        return [[self.col0[r], self.col1[r]] for r in range(self.rows)]

    def __repr__(self):
        R = self.rows
        lines = [f"Sand Drawer ({R}x2):"]
        for r in range(R):
            g0 = "v" if (r < R - 1 and self.gates0[r]) else " "
            g1 = "v" if (r < R - 1 and self.gates1[r]) else " "
            lines.append(f"  Row {r}: [{self.col0[r]:.1f}{g0} | {self.col1[r]:.1f}{g1}]")
        return "\n".join(lines)


def create_random_state(rows: int = 5, seed: Optional[int] = None) -> State:
    """
    Generate an initial state using the course probabilities:
    - 0.5 chance of being empty (0.0)
    - 0.3 chance of being full (1.0)
    - 0.2 chance of being half-full (0.5)
    Initial gates are all closed (False).
    """
    if seed is not None:
        random.seed(seed)
    values = [0.0, 1.0, 0.5]
    weights = [0.5, 0.3, 0.2]
    c0 = tuple(random.choices(values, weights=weights, k=rows))
    c1 = tuple(random.choices(values, weights=weights, k=rows))
    g0 = tuple(False for _ in range(rows - 1))
    g1 = tuple(False for _ in range(rows - 1))
    return State(c0, c1, g0, g1)


def create_teacher_state() -> State:
    """
    Create the illustrative 4x2 matrix presented by the professor in class:
    1 0
    0 1
    0 1
    1 0
    """
    return State(
        col0=(1.0, 0.0, 0.0, 1.0),
        col1=(0.0, 1.0, 1.0, 0.0),
        gates0=(False, False, False),
        gates1=(False, False, False)
    )


def open_vertical_gate(sand: Tuple[float, ...], gates: Tuple[bool, ...], gate_idx: int) -> Tuple[Tuple[float, ...], Tuple[bool, ...], float]:
    """
    Execute Action a: Open a vertical gate in one column.
    gate_idx:
      - 0 .. R-2: gate between row gate_idx and row gate_idx + 1
      - R-1: bottom gate draining to the outside world
    Returns: (new_sand, new_gates, cost)
    """
    R = len(sand)
    new_sand = list(sand)
    new_gates = list(gates)

    s_before = new_sand[gate_idx]

    if gate_idx == R - 1:
        # Bottom exit opened
        r = R - 1
        new_sand[r] = 0.0
        # All rows above connected via open gates drain out
        while r > 0 and new_gates[r - 1]:
            new_sand[r - 1] = 0.0
            new_gates[r - 1] = False
            r -= 1

        s_after = new_sand[gate_idx] # 0.0
        cost = 1.0 + 4.0 * (s_before + s_after)
        return tuple(new_sand), tuple(new_gates), cost

    else:
        # Internal gate between row r and r+1
        r = gate_idx
        new_gates[r] = True

        # Find continuous chain of open gates containing r and r+1
        top_r = r
        while top_r > 0 and new_gates[top_r - 1]:
            top_r -= 1

        bot_r = r + 1
        while bot_r < R - 1 and new_gates[bot_r]:
            bot_r += 1

        # Total sand in rows top_r .. bot_r
        total_sand = sum(new_sand[i] for i in range(top_r, bot_r + 1))

        # Gravity settles sand down to lowest possible rows
        rem = total_sand
        for i in range(bot_r, top_r - 1, -1):
            amount = min(1.0, rem)
            new_sand[i] = amount
            rem -= amount

        # A plank can close if no sand is trapped between cell k and k+1 (cell k is empty)
        for k in range(top_r, bot_r):
            if new_sand[k] == 0.0:
                new_gates[k] = False
            else:
                new_gates[k] = True

        s_after = new_sand[r]
        cost = 1.0 + 4.0 * (s_before + s_after)
        return tuple(new_sand), tuple(new_gates), cost


def open_side_gate(state: State, r: int) -> Tuple[State, float]:
    """
    Execute Action b: Open side gate at row r.
    Equalizes sand in row r between columns: (c0 + c1) / 2.
    Cost: 1.0.
    """
    new_c0 = list(state.col0)
    new_c1 = list(state.col1)

    avg = (new_c0[r] + new_c1[r]) / 2.0
    new_c0[r] = avg
    new_c1[r] = avg

    cost = 1.0
    return State(tuple(new_c0), tuple(new_c1), state.gates0, state.gates1), cost


def get_successors(state: State) -> List[Tuple[Action, State, float]]:
    """
    Generate all valid non-redundant successor states and their costs.
    Prunes:
    - Re-opening an already jammed vertical gate.
    - Opening a vertical gate when no sand exists at or above it.
    - Side gates on cells that don't produce valid {0, 0.5, 1} states
      (e.g., only {1.0, 0.0} pairs equalize to {0.5, 0.5}).
    """
    R = state.rows
    successors = []

    # 1. Vertical gates in Column 0
    for g in range(R):
        if g < R - 1 and state.gates0[g]:
            continue
        if g < R - 1:
            top_r = g
            while top_r > 0 and state.gates0[top_r - 1]:
                top_r -= 1
            if sum(state.col0[i] for i in range(top_r, g + 1)) == 0.0:
                continue
        else:
            top_r = R - 1
            while top_r > 0 and state.gates0[top_r - 1]:
                top_r -= 1
            if sum(state.col0[i] for i in range(top_r, R)) == 0.0:
                continue

        new_sand, new_gates, cost = open_vertical_gate(state.col0, state.gates0, g)
        act = Action('vertical', 0, g, f"Flush col 0 gate {g}")
        next_st = State(new_sand, state.col1, new_gates, state.gates1)
        successors.append((act, next_st, cost))

    # 2. Vertical gates in Column 1
    for g in range(R):
        if g < R - 1 and state.gates1[g]:
            continue
        if g < R - 1:
            top_r = g
            while top_r > 0 and state.gates1[top_r - 1]:
                top_r -= 1
            if sum(state.col1[i] for i in range(top_r, g + 1)) == 0.0:
                continue
        else:
            top_r = R - 1
            while top_r > 0 and state.gates1[top_r - 1]:
                top_r -= 1
            if sum(state.col1[i] for i in range(top_r, R)) == 0.0:
                continue

        new_sand, new_gates, cost = open_vertical_gate(state.col1, state.gates1, g)
        act = Action('vertical', 1, g, f"Flush col 1 gate {g}")
        next_st = State(state.col0, new_sand, state.gates0, new_gates)
        successors.append((act, next_st, cost))

    # 3. Side gates (Action b)
    for r in range(R):
        c0, c1 = state.col0[r], state.col1[r]
        if (c0 == 1.0 and c1 == 0.0) or (c0 == 0.0 and c1 == 1.0):
            new_st, cost = open_side_gate(state, r)
            act = Action('side', None, r, f"Side gate row {r}")
            successors.append((act, new_st, cost))

    return successors
