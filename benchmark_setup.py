"""
Benchmarking search algorithms on 5x2 grid
"""
import time
from typing import Tuple, List, Optional
import heapq

# State representation:
# We can represent grid state as a tuple of length 10:
# (c0_r0, c0_r1, c0_r2, c0_r3, c0_r4, c1_r0, c1_r1, c1_r2, c1_r3, c1_r4)
# And open gates:
# (g0_0, g0_1, g0_2, g0_3, g1_0, g1_1, g1_2, g1_3) - booleans
# Or an immutable dataclass / tuple.
