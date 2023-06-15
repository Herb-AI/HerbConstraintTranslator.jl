from pyprogtree.decision_variables import DecisionVariables

def enforce_implied_constraints(dv: DecisionVariables):
    """
    Optional implied constraints for speed-ups
    """
    return [
        # Property of pre-order depth-first ordering
        [dv.parent[n] > n for n in range(dv.max_n - 1)],
    ]