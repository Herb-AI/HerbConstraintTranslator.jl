from pyprogtree.decision_variables import DecisionVariables

def enforce_empty_nodes(dv: DecisionVariables):
    """
    Enforces nodes before the `init_index` to be empty.
    """
    return [
        # Node is empty iff its before the initial index
        [(n < dv.init_index) == (dv.rule[n] == dv.g.EMPTY_RULE) for n in range(dv.max_n)],

        # Empties are leftmost tail
        [(n < dv.init_index).implies(dv.parent[n] == dv.init_index) for n in range(dv.max_n - 1)]
    ]