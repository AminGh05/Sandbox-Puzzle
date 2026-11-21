# Scratch script to explore teacher's exact trace

def cost_a(s, s_prime):
    return 1 + 4 * (s + s_prime)

print("Possible top-down costs:")
for s in [0, 0.5, 1.0]:
    for sp in [0, 0.5, 1.0]:
        print(f"s={s}, s'={sp} -> cost = {cost_a(s, sp)}")
