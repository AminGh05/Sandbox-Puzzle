import pickle, os

base = os.path.dirname(os.path.abspath(__file__))
d = pickle.load(open(os.path.join(base, "all_59049_results.pkl"), "rb"))
ks = list(d.keys())[:3]
print(len(d))
print(ks)
print([d[k] for k in ks])
