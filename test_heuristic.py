# Test heuristic functions against UCS
import heapq

# Candidate heuristics:
# h0: 0 (trivial, guaranteed admissible)
# h1: Total remaining sand M * 4 (if M > 0, 1 + 4*M? wait, let's verify)
# h2: Distance-weighted sand: sum_{r, c} sand[r, c] * (R - r) ? Wait, let's check!
# Let's test what the exact optimal costs are for many states.
