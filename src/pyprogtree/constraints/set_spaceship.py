from cpmpy import IfThenElse

from src.pyprogtree.constraints.custom_constraint import CustomConstraint

class SetSpaceShip(CustomConstraint):
    """
    Enforces `spaceship(n, m)` to take values in (-1, 0, 1) representing (<, =, >) for rule[n] and rule[m].
    It breaks ties by resursively considering its children.
    It assumes nodes are stored in post-order depth-first ordering,
    since the post-order depth-first ordering of node arities of a valid tree uniquely defines the structure of that tree.

    Example:
        spaceship(5, 10) == 0 implies that the entire subtrees rooted at node 5 and 10 are identical
    """
    def decompose(self):
        # Note that the spaceship_helper is lower triangular and is only constrained for (n, m, k) such that:
        # max_n > n > m >= k
        return [
            # Set the spaceship operator for the leaf nodes
            [[
                (self.dv.rule[n] < self.dv.rule[m]).implies(self.dv.spaceship_helper[n, m, 0] == -1) &
                (self.dv.rule[n] > self.dv.rule[m]).implies(self.dv.spaceship_helper[n, m, 0] == 1) &
                (self.dv.rule[n] == self.dv.rule[m]).implies(self.dv.spaceship_helper[n, m, 0] == 0)
                for m in range(n)] for n in range(self.max_n - 1)],

            # Set the spaceship operator for the internal nodes, breaking ties up until k nodes back
            [[[
                IfThenElse(
                    self.dv.spaceship_helper[n, m, 0] == 0,
                    self.dv.spaceship_helper[n, m, k] == self.dv.spaceship_helper[n - 1, m - 1, k - 1],
                    self.dv.spaceship_helper[n, m, k] == self.dv.spaceship_helper[n, m, 0]
                )
                for k in range(1, m + 1)] for m in range(n)] for n in range(self.max_n - 1)],
        ]