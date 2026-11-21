"""
Let's formalize the state representation and transition function.

For a column c, we have:
sand amounts: [s_0, s_1, ..., s_{R-1}]
open_gates: boolean array of size R, where open_gates[r] indicates whether
gate r (between r and r+1 for r < R-1, or below R-1 for r = R-1) is open.
Wait, can a bottom gate ever be stuck open?
No, because outside has infinite capacity, so all sand exits, so gate R-1 always closes immediately after flushing!
So open_gates only needs to track gates 0 to R-2!

Wait! Does side gate action (Action b) need to know if vertical gates are open?
Can a side gate be opened if a vertical gate is stuck open?
Or does side gate only happen when no vertical gates are stuck open, or can it happen anytime?
In the teacher's example:
"Side gates approach:
1 + 1 = 2
7 + 9 + 9 + 5 = 30
3 + 5 + 5 = 13"
Here, both side gates were opened FIRST (at the start), before any top-down gates were opened!
"""

def test_step():
    pass
