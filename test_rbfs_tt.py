from environment import create_teacher_state
from heuristics import h_gravity
from environment import get_successors
import time

class RBFSNode:
    __slots__ = ('state', 'parent', 'action', 'cost', 'g', 'h', 'f')
    def __init__(self, state, parent=None, action=None, cost=0.0, g=0.0, h=0.0, f=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.g = g
        self.h = h
        self.f = f

def rbfs_with_tt(initial_state, max_nodes=100000):
    nodes_expanded = 0
    t0 = time.time()
    tt = {} # Transposition table: state -> best g

    def _rbfs(node, f_limit):
        nonlocal nodes_expanded
        nodes_expanded += 1
        if nodes_expanded > max_nodes:
            return None, float('inf')

        if node.state.is_goal():
            return node, 0.0

        if node.state in tt and node.g > tt[node.state]:
            return None, float('inf')
        tt[node.state] = node.g

        successors = []
        for act, next_st, act_cost in get_successors(node.state):
            g = node.g + act_cost
            if next_st in tt and g >= tt[next_st]:
                continue
            h = h_gravity(next_st)
            f = max(g + h, node.f)
            child = RBFSNode(next_st, parent=node, action=act, cost=act_cost, g=g, h=h, f=f)
            successors.append(child)

        if not successors:
            return None, float('inf')

        while True:
            successors.sort(key=lambda x: (x.f, x.h))
            best = successors[0]
            if best.f > f_limit:
                return None, best.f

            alternative = successors[1].f if len(successors) > 1 else float('inf')
            result, best.f = _rbfs(best, min(f_limit, alternative))
            if result is not None:
                return result, best.f

    h0 = h_gravity(initial_state)
    root = RBFSNode(initial_state, g=0.0, h=h0, f=h0)
    res, _ = _rbfs(root, float('inf'))
    dt = time.time() - t0
    return res, nodes_expanded, dt

st = create_teacher_state()
res, nodes, dt = rbfs_with_tt(st)
print(f"RBFS with TT: Result={res is not None}, Cost={res.g if res else None}, Nodes={nodes}, Time={dt:.3f}s")
