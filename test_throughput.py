import itertools
import random
import time

values = [0.0, 0.5, 1.0]
# How many states have zero sand in both columns? 1
# How many states have zero sand in one column? 243 + 243 - 1 = 485
# For these, side gates might be opened if one has 1.0 and other 0.0.

print("Testing throughput...")
