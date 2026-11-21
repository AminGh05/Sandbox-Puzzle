import multiprocessing as mp
import time
import itertools
from test_ultra_fast import ultra_fast_solve

def worker(pair):
    c0, c1 = pair
    cost, acts, b_acts = ultra_fast_solve(c0, c1)
    return (c0, c1, cost, acts, b_acts)

if __name__ == '__main__':
    values = [0.0, 0.5, 1.0]
    all_cols = list(itertools.product(values, repeat=5))
    pairs = []
    for i in range(len(all_cols)):
        for j in range(i, len(all_cols)):
            pairs.append((all_cols[i], all_cols[j]))
            if len(pairs) >= 500:
                break
        if len(pairs) >= 500:
            break

    print(f"Testing 500 pairs with ultra_fast_solve on {mp.cpu_count()} cores...")
    t0 = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        res = pool.map(worker, pairs, chunksize=50)
    dt = time.time() - t0
    print(f"500 pairs solved in {dt:.2f} seconds ({len(res)/dt:.1f} pairs/sec)!")
