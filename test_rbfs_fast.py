# Test RBFS with epsilon
from environment import create_teacher_state
from heuristics import h_gravity
from environment import get_successors
import time

class RBFSNode:
    __slots__ = ('state', 'parent', 'action', 'cost', 'g', 'h', 'f', 'id')
    def __init__(self, state, parent=None, action=None, cost=0.0, g=0.0, h=0.0, f=0.0, node_id=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.g = g
        self.h = h
        self.f = f
        self.id = node_id

def test_rbfs_fast(initial_state, max_nodes=50000):
    node_id_counter = 0
    nodes_expanded = 0
    t0 = time.time()

    def _rbfs(node, f_limit):
        nonlocal node_id_counter, nodes_expanded
        nodes_expanded += 1
        if nodes_expanded > max_nodes:
            return None, float('inf')

        if node.state.is_goal():
            return node, 0.0

        ancestor = node.parent
        ancestors = set()
        while ancestor:
            ancestors.add(ancestor.state)
            ancestor = ancestor.parent

        successors = []
        for act, next_st, act_cost in get_successors(node.state):
            if next_st in ancestors:
                continue
            g = node.g + act_cost
            h = h_gravity(next_st)
            f = max(g + h, node.f)
            node_id_counter += 1
            child = RBFSNode(next_st, parent=node, action=act, cost=act_cost, g=g, h=h, f=f, node_id=node_id_counter)
            successors.append(child)

        if not successors:
            return None, float('inf')

        while True:
            successors.sort(key=lambda x: (x.f, x.h, x.id))
            best = successors[0]
            if best.f > f_limit:
                return None, best.f

            # If alternative == best.f, allow a small margin to prevent ping-pong thrashing
            if len(successors) > 1:
                alternative = successors[1].f
                if alternative <= best.f:
                    # Give headroom so it explores deeper along this promising branch
                    effective_alt = max(alternative, best.f + 2.0)
                else:
                    effective_alt = alternative
            else:
                effective_alt = float('inf')

            result, best.f = _rbfs(best, min(f_limit, effective_alt))
            if result is not None:
                return result, best.f

    h0 = h_gravity(initial_state)
    root = RBFSNode(initial_state, g=0.0, h=h0, f=h0)
    res, _ = _rbfs(root, float('inf'))
    dt = time.time() - t0
    return res, nodes_expanded, dt

st = create_teacher_state()
res, nodes, dt = test_rbfs_fast(st)
print(f"RBFS fast: Result={res is not None}, Cost={res.g if res else None}, Nodes={nodes}, Time={dt:.3f}s")
