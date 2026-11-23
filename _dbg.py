import numpy as np, json
from environment import create_random_state
from heuristic_learned import extract_features

d = json.load(open("heuristic_weights.json"))
w = np.array(d["weights"])
fn = d["feature_names"]
# sanity: report top contributors for the worst state
st = create_random_state(rows=5, seed=10531)
phi = np.array(extract_features(st))
contrib = phi * w
for n, p, c in zip(fn, phi, contrib):
    if abs(c) > 1e-6:
        print(f"{n:<12} phi={p:8.3f}  w={w[fn.index(n)]:8.4f}  contrib={c:8.3f}")
print("raw =", phi @ w, " h* = 15.0")
