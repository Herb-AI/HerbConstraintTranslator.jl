from pyprogtree.decision_variables import DecisionVariables

def enforce_ancestor_rule(dv: DecisionVariables):
    """
    Enforces `ancestor_rule[n]` to align with all parents of node n.
    """
    return [
        [
            (d < dv.depth[n] - 1).implies(
                dv.ancestor_rule[n, d] == dv.ancestor_rule[dv.parent[n], d]
            ) for n in range(dv.max_n - 1) for d in range(dv.max_depth)
        ],

        [dv.ancestor_rule[n, dv.depth[n] - 1] == dv.rule[dv.parent[n]]
         for n in range(dv.max_n - 1)],

        [(d >= dv.depth[n]).implies(dv.ancestor_rule[n, d] == -1)
        for n in range(dv.max_n - 1) for d in range(dv.max_depth)],
    ]