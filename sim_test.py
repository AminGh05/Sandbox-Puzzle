# Let's explore the state space and mechanics of gates

"""
Let's check the gates for a grid of R rows and C=2 columns:
For each column c in {0, 1}:
  Vertical gates:
    Gate(r, r+1, c) for r in 0..R-2  (between rows r and r+1)
    Gate(R-1, OUT, c)               (bottom exit)
  Total vertical gates = C * R = 2 * R (for R=5, that's 10 vertical gates; for R=4, 8 vertical gates)

Horizontal (side) gates:
  SideGate(r) for r in 0..R-1 (between col 0 and col 1 at row r)
  Total side gates = R (for R=5, 5 side gates; for R=4, 4 side gates)
"""
print("Gate definitions")
