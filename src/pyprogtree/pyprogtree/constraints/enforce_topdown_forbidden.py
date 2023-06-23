from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Enforces the topdown forbidden constraint. It generates all the ranges the ancestor_rule array could
be divided into, and checks if for all these ranges, at least one of the constraints holds. These
constraints state there is less than the repeats in the sequence of this rule, in this sequence. 
"""
def enforce_topdown_forbidden(dv: DecisionVariables):   
    constraints = []
    for n in range(dv.max_n-1):
        for indexing, sequence in dv.g.TOPDOWN_FORBIDDEN:
            constraints.append(
                any(
                    [dv.topdown_rule_indexes[n][sequence[i]][indexing[i]] == (dv.max_depth+1) for i in range(len(sequence))]
                ) | any(
                    [(dv.topdown_rule_indexes[n][sequence[i]][indexing[i]] >= dv.topdown_rule_indexes[n][sequence[i+1]][indexing[i+1]]) for i in range(len(sequence)-1)]
            )   )
            
    return constraints