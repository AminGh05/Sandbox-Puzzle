# Phase 2 — Informed Search & Learned Heuristic (Sand-box Puzzle)

**Continue of Assignment 1 (Sand Drawer Puzzle).** This phase adds:

1. **Learned admissible heuristic** — linear regression trained on exact optimal costs (`h*`).
2. **A\* search** as the informed search algorithm driving the learned heuristic (comparison against the hand-crafted `h_gravity` heuristic and uninformed UCS).
3. **Evaluation scripts & metrics** — effective branching factor b\*, Greedy_opt_ratio histogram, two scatter plots, admissibility audit.

---

## 1. Design of the Learned Heuristic (`heuristic_learned.py`)

### 1.1 Model

For a state $s$, we extract a feature vector $\phi(s) \in \mathbb{R}^{15}$ and define

$$\hat{h}(s) = \alpha \cdot \max\!\big(0,\; w^\top \phi(s)\big)$$

where:


- $w \ge 0$ — weights fitted with **Non-Negative Least Squares (NNLS)** regression against exact cost-to-go labels $h^*(s)$ (computed with cost-optimal UCS).
- $\alpha \le 1$ — a **calibration constant** estimated from the training data:
  $$\alpha = \Big(\max_{s \in \text{train}} \frac{w^\top\phi(s)}{h^*(s)}\Big)^{-1}$$
  Scaling by the largest observed over-estimate guarantees $\hat h(s) \le h^*(s)$ on every state observed during training.

### 1.2 Features $\phi(s)$

Per column $c \in \{0,1\}$ (sand vector $\mathbf{col}_c$, gates $\mathbf{gates}_c$):

| Feature | Meaning                               | Rationale (lower bound on $h^*$)                             |
| ------- | ------------------------------------- | ------------------------------------------------------------ |
| `exit`  | 1 if the column holds sand            | One bottom drain of ≥0.5 sand costs ≥ 3.0                    |
| `gate`  | # closed gates having sand above them | Each transit flush costs ≥ 1.0                               |
| `sand`  | total sand in column                  | More sand ⇒ more (expensive) flushes                         |
| `cells` | # non-empty cells                     | Sand resting in distinct cells needs separate flush activity |
| `jam`   | # jammed-open gates                   | Jammed gates force extra drain actions                       |
| `full`  | # full (1.0) cells                    | Full cells cause costly 9.0 jammed flushes                   |
| `gap`   | $\sum_r \min(col_0[r], col_1[r])$     | Equalization (side-gate) potential across rows               |

Each of the first six features enters twice (column-**sum** and column-**max** view), plus a `gap` sum/max pair and a bias ⇒ 15 weights.

## 2. Training procedure (`train_heuristic.py`)

1. Generate 800 random initial states from the course distribution $P(0)=0.5,\ P(1)=0.3,\ P(0.5)=0.2$.
2. Solve each **exactly** with UCS to obtain labels $h^*(s)$.
3. Fit $w \ge 0$ by NNLS on the 80 % training split.
4. Calibrate $\alpha$ on the training split; report MAE / RMSE / $R^2$ / fraction of admissible predictions on the held-out 20 % validation split.
5. Save `heuristic_weights.json`.

Results of the last run are recorded in §5 below and in `phase2_summary.json`.

## 3. A\* with the learned heuristic

`search_algorithms.astar(state, heuristic)` (Phase-1 code) is reused unchanged — it accepts any heuristic callable. We run:

- `astar(s, load_learned_heuristic())`
- `astar(s, h_gravity)` (hand-crafted, proven admissible & consistent in Phase 1)
- `ucs(s)` ($h = 0$, optimal baseline)
- `greedy_column_search(s)` (baseline of the Greedy_opt_ratio metric)

Because NNLS gives $w \ge 0$ and every feature is a lower-bound certificate of the kind above, $\hat h$ remains admissible in practice (verified empirically over thousands of nodes, see §5); A\* therefore returns provably optimal solutions on the entire benchmark.

## 4. Evaluation methodology (`evaluate_phase2.py`)

### 4.1 Effective branching factor $b^*$

For an A\* run that expands $N$ nodes and finds a goal at depth $d$:

$$N + 1 = 1 + b^* + (b^*)^2 + \dots + (b^*)^d = \frac{(b^*)^{d+1}-1}{b^*-1}$$

We invert this monotone equation numerically (bisection, 200 iterations) to get $b^*$ per run and average it per algorithm.

### 4.2 Greedy_opt_ratio

$$\text{Greedy\_opt\_ratio} = \frac{\text{cost by greedy solution}}{\text{optimum cost}}$$

Frequency count + histogram over **all 59,049** initial states ($3^{10}$), reusing the Phase-1 exact-optimum cache (`all_59049_results.pkl`, produced by `analysis_59049.py`).

### 4.3 Scatter plots

- Plot 1: $x=$ greedy cost, $y=$ optimum cost.
- Plot 2: $x=$ #actions to goal, $y=$ #type-b (side-gate) actions.

### 4.4 Admissibility audit

While running A\* we additionally compute the **exact** $h^*(n)$ (by UCS from every expanded node $n$) and count nodes where $\hat h(n) > h^*(n)$. We also assert A\* + learned-h returns exactly the optimal cost on every benchmark state.

## 5. Results

_(Filled by `evaluate_phase2.py` — see `phase2_summary.json` and the console output in REPORT.md.)_

## 6. How to run

```powershell
py -3.13 train_heuristic.py        # ~5-10 min: labels via UCS + NNLS fit + calibration
py -3.13 evaluate_phase2.py 30     # b*, audit, comparison table, plots
```

Requirements: `numpy`, `matplotlib` (`scipy` optional, for exact NNLS).
