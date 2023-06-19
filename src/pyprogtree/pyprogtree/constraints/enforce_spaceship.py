from cpmpy import IfThenElse
from pyprogtree.decision_variables import DecisionVariables

def enforce_spaceship(dv: DecisionVariables):
    """
    Enforces `spaceship(n, m)` to take values in (-1, 0, 1) representing (<, =, >) for rule[n] and rule[m] and breaks ties by resursively considering its children.
    It assumes nodes are stored in post-order depth-first ordering, since the post-order depth-first ordering of node arities of a valid tree uniquely defines the structure of that tree.

    Example:
        spaceship(5, 10) == 0 implies that the entire subtrees rooted at node 5 and 10 are identical.
    """
    # Note that the spaceship_helper is lower triangular and is only constrained for (n, m, k) such that:
    # max_n > n > m >= k
    return [
        # Set the spaceship operator for the leaf nodes
        [
            (dv.rule[n] < dv.rule[m]).implies(dv.spaceship_helper(n, m, 0) == -1) &
            (dv.rule[n] > dv.rule[m]).implies(dv.spaceship_helper(n, m, 0) == 1) &
            (dv.rule[n] == dv.rule[m]).implies(dv.spaceship_helper(n, m, 0) == 0)
        for n in range(dv.max_n - 1) for m in range(n)],

        # Set the spaceship operator for the internal nodes, breaking ties up until k nodes back
        [
            IfThenElse(
                dv.spaceship_helper(n, m, 0) == 0,
                dv.spaceship_helper(n, m, k) == dv.spaceship_helper(n - 1, m - 1, k - 1),
                dv.spaceship_helper(n, m, k) == dv.spaceship_helper(n, m, 0)
            )
        for n in range(dv.max_n - 1) for m in range(n) for k in range(1, m + 1)],

        # Make the matrix skew symmetric
        [
            dv.spaceship_helper(n, m, k) == -dv.spaceship_helper(m, n, k)
        for n in range(dv.max_n - 1) for m in range(n) for k in range(dv.max_n - 1)],

        # Reflexive: n == n
        [
            dv.spaceship_helper(n, n, k) == 0
        for n in range(dv.max_n - 1) for k in range(dv.max_n - 1)],

        # Break symmetry: define spaceship for all k. (tie breaking stops at k>m: borrow value from k=m)
        [
            dv.spaceship_helper(n, m, k) == dv.spaceship_helper(n, m, m)
        for n in range(dv.max_n - 1) for m in range(n + 1) for k in range(m + 1, dv.max_n - 1)]
    ]