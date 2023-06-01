import numpy as np

from src.pyprogtree.constraints.custom_constraint import CustomConstraint
from src.pyprogtree.decision_variables import DecisionVariables


class DepthFirstOrdering(CustomConstraint):
    """
    Enfoce a lexicographic ordering.

    Note: might suffer from integer overflow issue as the sums quickly get very large.
    """

    def __init__(self, dv: DecisionVariables, *args):
        super().__init__(dv, *args)
        self.base = np.array([(self.g.MAX_ARITY + 1) ** i for i in range(self.max_depth)][::-1])

    def decompose(self):
        return [sum(self.dv.ancestor_path[n] * self.base) <=
             sum(self.dv.ancestor_path[n + 1] * self.base)
       for n in range(self.max_n - 1)]