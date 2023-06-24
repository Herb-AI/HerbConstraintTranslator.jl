from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *
import numpy as np

"""
The leftright order constraints are enforced, by having the occurrences of the rules in the
sequence in the same order in indexes in leftright_rule_indexes.
"""
def enforce_leftright_ordered(dv: DecisionVariables): 
    return [
        (   dv.leftright_rule_indexes[sequence[i  ]][indexing[i  ]] 
         <= dv.leftright_rule_indexes[sequence[i-1]][indexing[i-1]])

         for indexing, sequence in dv.g.LEFTRIGHT_ORDERED
         for i in range(1, len(sequence))
    ]