from src.pyprogtree.decision_variables import DecisionVariables

def enforce_treesize(dv: DecisionVariables):
    """
    Enforces `treesize[n]` to the number of nodes in the subtree rooted at node n
    """
    return [
        # Calculate the treesize for each node
        [dv.treesize[n] ==
            1 + sum([((dv.parent[child] == n) & (child >= dv.init_index)) * dv.treesize[child]
        for child in range(dv.max_n - 1)]) for n in range(dv.max_n)],

        # Implicit constraint that fixes the treesize of the root, to potentially improve performance
        dv.treesize[dv.max_n - 1] == dv.max_n - dv.init_index
    ]