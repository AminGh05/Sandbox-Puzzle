import math
from test_discrete import State, get_successors_discrete

def h_gravity(state: State) -> float:
    if state.is_goal():
        return 0.0
    R = len(state.col0)
    h = 0.0
    for col, gates in [(state.col0, state.gates0), (state.col1, state.gates1)]:
        if sum(col) == 0.0:
            continue
        col_h = 3.0
        for r in range(R - 1):
            if sum(col[:r+1]) > 0.0 and not gates[r]:
                col_h += 1.0
        h += col_h
    return h

class RBFSNode:
    def __init__(self, state, parent=None, action=None, g=0.0, h=0.0, f=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        self.f = f

def rbfs(initial_state: State, max_nodes=100000):
    nodes_expanded = [0]

    def _rbfs(node, f_limit):
        nodes_expanded[0] += 1
        if nodes_expanded[0] > max_nodes:
            return None, float('inf')

        if node.state.is_goal():
            return node, 0.0

        successors = []
        for act, next_st, act_cost in get_successors_discrete(node.state):
            g = node.g + act_cost
            h = h_gravity(next_st)
            f = max(g + h, node.f)
            child = RBFSNode(next_st, parent=node, action=(act, act_cost), g=g, h=h, f=f)
            successors.append(child)

        if not successors:
            return None, float('inf')

        while True:
            successors.sort(key=lambda x: x.f)
            best = successors[0]
            if best.f > f_limit:
                return None, best.f
            alternative = successors[1].f if len(successors) > 1 else float('inf')
            result, best.f = _rbfs(best, min(f_limit, alternative))
            if result is not None:
                return result, best.f

    h0 = h_gravity(initial_state)
    root = RBFSNode(initial_state, g=0.0, h=h0, f=h0)
    result_node, _ = _rbfs(root, float('inf'))

    if result_node:
        path = []
        curr = result_node
        while curr.parent:
            path.append((curr.action[0], curr.action[1], curr.state))
            curr = curr.parent
        path.reverse()
        return result_node.g, path, nodes_expanded[0]
    return None, None, nodes_expanded[0]

# Teacher's example
init_state = State(
    col0=(1.0, 0.0, 0.0, 1.0),
    col1=(0.0, 1.0, 1.0, 0.0),
    gates0=(False, False, False),
    gates1=(False, False, False)
)

cost, path, nodes = rbfs(init_state)
print(f"RBFS on teacher example: Cost = {cost}, Nodes = {nodes}")
if path:
    for act, c, s in path:
        print(f"  {act.description} (cost={c})")
