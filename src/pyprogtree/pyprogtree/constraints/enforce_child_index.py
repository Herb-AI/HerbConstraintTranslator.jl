from cpmpy import Count
from pyprogtree.decision_variables import DecisionVariables

def enforce_child_index(dv: DecisionVariables):
    """
    Enforces `child_index` to index non-empty children of the same parent.

    Example:
        nodes 5, 6 and 9 are children of parent 17 -->
        child_index[5] = 0
        child_index[6] = 1
        child_index[9] = 2
    """
    return [
        # Child index of the root is 0
        dv.child_index[dv.max_n-1] == 0,

        dv.child_index[dv.max_n-2] == 0,

        # Indexing children of the same parent
        [(n >= dv.init_index).implies(dv.child_index[n] == Count(dv.parent[n+1:], dv.parent[n]))
        for n in range(1, dv.max_n - 2)],

        # Child index of empty nodes
        [(n < dv.init_index).implies(dv.child_index[n] == 0) for n in range(0, dv.max_n - 1)]
    ]