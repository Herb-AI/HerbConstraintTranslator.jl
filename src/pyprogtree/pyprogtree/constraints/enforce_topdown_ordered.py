from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Enforces the topdown ordered constraint. Either the first occurrence of the last in the sequence
is max_depth+1 or every index occurrence of the rule in the sequence needs to be in increasing order.
"""
def enforce_topdown_ordered(dv: DecisionVariables): 
    return [
        (
            (dv.topdown_rule_indexes[n][sequence[-1]][0] == (dv.max_depth+1)) | 
            
            all(
                [(dv.topdown_rule_indexes[n][sequence[i  ]][indexing[i  ]] 
                < dv.topdown_rule_indexes[n][sequence[i+1]][indexing[i+1]]
                ) for i in range(len(sequence)-1)]
            )
        )
        for n in range(dv.max_n-1)
        for indexing, sequence in dv.g.TOPDOWN_ORDERED
    ]