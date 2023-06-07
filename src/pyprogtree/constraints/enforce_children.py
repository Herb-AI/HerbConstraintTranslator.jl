def index(dv: DecisionVariables, node_index, child_index):
    return node_index*dv.g.MAX_ARITY + child_index

def enforce_children(dv: DecisionVariables):
    """
    Enforces children[n,i] to contain the ith child of node n
    """
    return [
        [dv.children[index(dv, dv.parent[n], dv.child_index[n])] == n  for n in range(dv.max_n-1)],
        [(i >= dv.arity[n]).implies(dv.children[index(dv, n, i)] == 0) for n in range(dv.max_n-1) for i in range(dv.g.MAX_ARITY)]
    ]