# Script to explore side-gate sequences for the 4x2 grid
import itertools

# Let's inspect what happens if side gates are opened
# Grid is 4 rows, 2 cols
# Row 0: [1, 0]
# Row 1: [0, 1]
# Row 2: [0, 1]
# Row 3: [1, 0]

# Side gate on row r:
# [1, 0] -> [0.5, 0.5] (cost 1)
# [0, 1] -> [0.5, 0.5] (cost 1)

# Notice in teacher's notes:
# "Side gates approach (here, might be optimum)
# 1+1=2 7+9+9+5=30 3+5+5=13
# ==> 45"

# Where does 3+5+5=13 come from?
# 3 is 1 + 4*(0.5 + 0)
# 5 is 1 + 4*(1 + 0) or 1 + 4*(0.5 + 0.5)
# 5 is 1 + 4*(1 + 0)
# Total sand in that column: 0.5 + 0.5 = 1.0?
# Wait! In 3+5+5=13, how much sand was there?
# If row 0 had 0.5, row 1 had 0.5:
# Flush row 0 -> 1: s=0.5, s'=0 -> cost 3. Row 1 now has 1.0!
# Flush row 1 -> 2: s=1.0, s'=0 -> cost 5. Row 2 now has 1.0!
# Flush row 2 -> 3: s=1.0, s'=0 -> cost 5. Row 3 now has 1.0!
# Wait! Then row 3 still has 1.0! That would need another flush out (cost 5)!
# But wait, what if the column was:
# Row 1: 0.5, Row 2: 0.5?
# Let's write a simulation!
