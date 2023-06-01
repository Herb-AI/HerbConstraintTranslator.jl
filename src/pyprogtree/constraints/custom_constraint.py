from src.pyprogtree.decision_variables import DecisionVariables

from abc import ABC
from cpmpy.expressions.globalconstraints import GlobalConstraint

class CustomConstraint(GlobalConstraint, ABC):
    def __init__(self, dv: DecisionVariables, *args):
        """
        Base Class of a constraint that has access to all decision variables
        :param dv:      all decision variables in the model.
        :param args:    additional arguments.
        """
        super().__init__(self.__class__.__name__, args)
        self.dv = dv
        self.g = dv.g
        self.min_n = dv.min_n
        self.max_n = dv.max_n
        self.max_depth = dv.max_depth

    def value(self):
        return self.decompose().value()