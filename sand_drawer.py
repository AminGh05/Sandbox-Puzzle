"""
sand_drawer.py
Formal definition of the Sand Drawer puzzle environment.
Grid: R rows, 2 columns (default R=5, columns=2).
Values: 0.0 (empty), 0.5 (half-full), 1.0 (full).
"""

from typing import Tuple, List, Dict, Optional, NamedTuple
import math

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
        return (self.col0 == other.col0 and
                self.col1 == other.col1 and
                self.gates0 == other.gates0 and
                self.gates1 == other.gates1)

    def is_goal(self) -> bool:
        return (not any(self.col0) and not any(self.col1) and
                not any(self.gates0) and not any(self.gates1))

    def total_sand(self) -> float:
        return sum(self.col0) + sum(self.col1)

    def __repr__(self):
        R = len(self.col0)
        lines = []
        for r in range(R):
            g0 = "v" if (r < R-1 and self.gates0[r]) else " "
            g1 = "v" if (r < R-1 and self.gates1[r]) else " "
            lines.append(f"[{self.col0[r]:.1f}{g0} | {self.col1[r]:.1f}{g1}]")
        return "State:\n" + "\n".join(lines)


def open_vertical_gate(sand: Tuple[float, ...], gates: Tuple[bool, ...], gate_idx: int) -> Tuple[Tuple[float, ...], Tuple[bool, ...], float]:
    """
    Open vertical gate in a single column.
    gate_idx: 0..R-2 (between row r and r+1), or R-1 (bottom exit).
    Returns (new_sand, new_gates, cost).
    """
    R = len(sand)
    new_sand = list(sand)
    new_gates = list(gates)

    s_before = new_sand[gate_idx]

    if gate_idx == R - 1:
        # Bottom gate opens!
        r = R - 1
        new_sand[r] = 0.0
        while r > 0 and new_gates[r - 1]:
            new_sand[r - 1] = 0.0
            new_gates[r - 1] = False
            r -= 1
        s_after = new_sand[gate_idx]
        cost = 1.0 + 4.0 * (s_before + s_after)
        return tuple(new_sand), tuple(new_gates), cost

    else:
        r = gate_idx
        new_gates[r] = True

        # Find connected component of open gates containing r and r+1
        top_r = r
        while top_r > 0 and new_gates[top_r - 1]:
            top_r -= 1

        bot_r = r + 1
        while bot_r < R - 1 and new_gates[bot_r]:
            bot_r += 1

        total_sand = sum(new_sand[i] for i in range(top_r, bot_r + 1))

        # Gravity settles sand to lowest rows (capacity 1.0 per row)
        rem = total_sand
        for i in range(bot_r, top_r - 1, -1):
            amount = min(1.0, rem)
            new_sand[i] = amount
            rem -= amount

        # Unjam gates where upper cell became 0
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
    Open side gate at row r.
    Equalizes sand in row r: (c0[r] + c1[r]) / 2.
    Cost = 1.0.
    """
    R = len(state.col0)
    new_c0 = list(state.col0)
    new_c1 = list(state.col1)

    avg = (new_c0[r] + new_c1[r]) / 2.0
    new_c0[r] = avg
    new_c1[r] = avg

    cost = 1.0
    # Side gate doesn't change vertical gates status directly
    return State(tuple(new_c0), tuple(new_c1), state.gates0, state.gates1), cost


class Action(NamedTuple):
    type: str  # 'vertical' or 'side'
    col: Optional[int]  # 0 or 1 for vertical, None for side
    index: int  # row or gate index
    description: str


def get_successors(state: State) -> List[Tuple[Action, State, float]]:
    """
    Generate all valid non-redundant successor states and their costs.
    """
    R = len(state.col0)
    successors = []

    # 1. Vertical gate actions for Column 0
    for g in range(R):
        # Redundancy checks:
        # If g < R - 1 and gate g is already open: skip
        if g < R - 1 and state.gates0[g]:
            continue
        # If opening g moves no sand (s_before == 0 and no open gates above with sand): skip
        # Specifically, check if there is any sand in the connected component above g
        if g < R - 1:
            # Check if any sand in row g or connected above
            top_r = g
            while top_r > 0 and state.gates0[top_r - 1]:
                top_r -= 1
            if sum(state.col0[i] for i in range(top_r, g + 1)) == 0.0:
                continue
        else:
            # Bottom gate
            if state.col0[R - 1] == 0.0:
                continue

        new_sand, new_gates, cost = open_vertical_gate(state.col0, state.gates0, g)
        act = Action('vertical', 0, g, f"Flush col 0 gate {g}")
        next_state = State(new_sand, state.col1, new_gates, state.gates1)
        successors.append((act, next_state, cost))

    # 2. Vertical gate actions for Column 1
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
            if state.col1[R - 1] == 0.0:
                continue

        new_sand, new_gates, cost = open_vertical_gate(state.col1, state.gates1, g)
        act = Action('vertical', 1, g, f"Flush col 1 gate {g}")
        next_state = State(state.col0, new_sand, state.gates0, new_gates)
        successors.append((act, next_state, cost))

    # 3. Side gate actions
    for r in range(R):
        # Non-redundant only if col0[r] != col1[r]
        if state.col0[r] != state.col1[r]:
            next_state, cost = open_side_gate(state, r)
            act = Action('side', None, r, f"Side gate row {r}")
            successors.append((act, next_state, cost))

    return successors
