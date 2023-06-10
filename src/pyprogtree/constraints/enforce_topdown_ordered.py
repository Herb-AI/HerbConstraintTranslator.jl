from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Retricts the topdown_rule_index values in two ways:
    1. The index at which a rule occurs, needs to be great enough to fit the entire order 
        coming before.
    2. From where the rule path is long enough to contain the entire rule order, the last rule
        in the order doesn't occur, or the indexes corresponding to the rules in the constraint 
        need to be in strictly ascending order.
"""
def enforce_topdown_ordered(dv: DecisionVariables): 
    return [
        [
            dv.topdown_rule_index[n,r] > idx
            for tdo in enumerate(dv.g.TOPDOWN_ORDERED)
            for n in range(dv.max_n-1)
            for idx, r in enumerate(tdo[1:])
        ],
        [
                (
                    all([(dv.topdown_rule_index[j, tdo[k]] 
                    <= dv.topdown_rule_index[j, tdo[k+1]])
                    for k in range(len(tdo)-1)])
                )
            for tdo in dv.g.TOPDOWN_ORDERED 
            for j, rule_path in enumerate(dv.ancestor_rule) 
            if len(tdo) < len(rule_path)
        ]
    ]