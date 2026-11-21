# Test partial order reduction (commuting actions)
import sys, time
sys.path.append('C:/Users/mogho/.gemini/antigravity/scratch/sand_box_puzzle')
from environment import State, get_successors
from test_col_solver import solve_col

# If state has no open side gates, and col0 has sand:
# Can we prioritize col0 actions, or if side gate is not opened, solve col0 then col1?
print("Testing partial-order concept...")
