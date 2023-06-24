from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *
import numpy as np

"""
Enforces the leftright order in two ways:
    1. The kth rule in the sequence should not occur if there are not k nodes before to fit the
       entire sequence.
    2. If the kth rule in the sequence occurs, all rules before it in the sequence must have 
       occurred earlier in the ordering. In this case the ordering makes it after it in the
       rule decision variable.
"""
def enforce_leftright_ordered(dv: DecisionVariables): 
    constraints = []
    for indexing, sequence in dv.g.LEFTRIGHT_ORDERED:
        for i in range(1, len(sequence)):
            constraints.append((dv.leftright_rule_indexes[sequence[i]][indexing[i]] <= dv.leftright_rule_indexes[sequence[i-1]][indexing[i-1]]))

    return constraints