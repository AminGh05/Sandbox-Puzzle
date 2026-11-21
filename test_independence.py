"""
Let's explore optimizing the search for batch evaluation.
"""
import itertools
from test_col_solver import solve_col

# Notice:
# In an initial state (col0, col1), all vertical gates are False.
# If col0 and col1 have no rows with {0.0, 1.0}, can ANY side gate EVER be opened?
# Let's check:
# If no row has {0.0, 1.0}:
# Rows can be:
# [0, 0], [0.5, 0.5], [1, 1], [0.5, 0], [0, 0.5], [1, 0.5], [0.5, 1].
# In none of these can a side gate be opened initially!
# Can a side gate be opened after vertical flushes?
# If col0 only has {0, 0.5} and col1 only has {0, 0.5}, sand can NEVER become 1.0!
# So side gate is NEVER possible!
# In that case, the two columns are 100% INDEPENDENT throughout the entire solve!
# Optimum cost is EXACTLY col_opt[col0] + col_opt[col1]!
# Optimum actions = col_act[col0] + col_act[col1]!
# Action b count = 0!
