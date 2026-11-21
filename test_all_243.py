import itertools
import time
from test_col_solver import solve_col

values = [0.0, 0.5, 1.0]
all_cols = list(itertools.product(values, repeat=5))
print(f"Total single column configurations: {len(all_cols)}")

t0 = time.time()
col_cache = {}
for c in all_cols:
    col_cache[c] = solve_col(c)
dt = time.time() - t0
print(f"Computed all 243 single column optimal solutions in {dt:.3f} seconds!")
