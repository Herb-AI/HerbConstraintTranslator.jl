from pyprogtree.decision_variables import DecisionVariables
def enforce_ancestor_path(dv: DecisionVariables):
    """
    Enforces `ancestor_path[n, d]` to store the `child_index[m]` of all parents m of node n
    """
    return [
        # Fix ancestor path of the root
        [dv.ancestor_path[dv.max_n - 1, d] == -1 for d in range(dv.max_depth)],

        # Enforce each node's path to be an extension of its parents path
        [
            (d < dv.depth[n] - 1).implies(
                dv.ancestor_path[n, d]
                == dv.ancestor_path[dv.parent[n], d])
            for n in range(dv.max_n - 1) for d in range(dv.max_depth)
        ],

        # Enforce each non-root node's last path symbol to be its child index
        [dv.ancestor_path[n, dv.depth[n] - 1] == dv.child_index[n] for n in range(dv.max_n - 1)],

        # Enforce the remaining path symbols to be max_arity
        [
            (d >= dv.depth[n]).implies(
                dv.ancestor_path[n, d] == -1
            )
            for n in range(dv.max_n - 1) for d in range(dv.max_depth)
        ],
    ]