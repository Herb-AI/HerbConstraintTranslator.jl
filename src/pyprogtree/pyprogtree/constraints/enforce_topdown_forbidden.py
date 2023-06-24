from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Enforces the topdown forbidden constraint. Either any of the rules in the sequence don't occur
or they need to be out of order.
"""
def enforce_topdown_forbidden(dv: DecisionVariables):   
    return [
        (any(
            [   dv.topdown_rule_indexes[n][sequence[i  ]][indexing[i  ]] 
                == (dv.max_depth+1) 
                
             for i in range(len(sequence))]
        ) | any(
            [(  dv.topdown_rule_indexes[n][sequence[i  ]][indexing[i  ]] 
              > dv.topdown_rule_indexes[n][sequence[i+1]][indexing[i+1]]) 
              
              for i in range(len(sequence)-1)]
        ))
        for n in range(dv.max_n-1)
        for indexing, sequence in dv.g.TOPDOWN_FORBIDDEN

    ]