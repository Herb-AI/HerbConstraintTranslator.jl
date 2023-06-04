import numpy as np
from src.pyprogtree.decision_variables import DecisionVariables

def enforce_first_ordering(dv: DecisionVariables):
    """
    Enfoce a lexicographic ordering.

    Note: might suffer from integer overflow issue as the sums quickly get very large.
    """
    base = np.array([(dv.g.MAX_ARITY + 1) ** i for i in range(dv.max_depth)][::-1])
    return [sum(dv.ancestor_path[n] * base) <= sum(dv.ancestor_path[n + 1] * base) for n in range(dv.max_n - 1)]