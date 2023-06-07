from src.pyprogtree.decision_variables import DecisionVariables

def enforce_children(dv: DecisionVariables):
    """
    Enforces children[n,i] to contain the ith child of node n
    """
    return [
        [dv.children[dv.parent[n]*dv.g.MAX_ARITY + dv.child_index[n]] == n  for n in range(dv.max_n-1)],
        [(i >= dv.arity[n]).implies(dv.children[n*dv.g.MAX_ARITY + i] == 0) for n in range(dv.max_n-1) for i in range(dv.g.MAX_ARITY)]
    ]