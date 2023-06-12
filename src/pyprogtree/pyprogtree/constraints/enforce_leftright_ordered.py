from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Retricts the leftright_rule_index values in two ways:
    1. The kth rule in the sequence should not occur if there are not k nodes before to fit the
        entire sequence.
    2. For every leftright ordered constraint, the kth index should be less than the k+1th 
        index for that rule.
"""
def enforce_leftright_ordered(dv: DecisionVariables): 
    return [
        [
            (dv.rule[n] != lro[r])

            for lro in dv.g.LEFTRIGHT_ORDERED
            for n in range(dv.max_n-len(lro)+1, dv.max_n) 

            if dv.max_n-n < len(lro)
            for r in range(dv.max_n-n, len(lro))
        ], 
        [
            (dv.leftright_rule_index[lro[r]] 
            <= dv.leftright_rule_index[lro[r+1]]) 

            for lro in dv.g.LEFTRIGHT_ORDERED
            for r in range(len(lro)-1)
        ]
    ]