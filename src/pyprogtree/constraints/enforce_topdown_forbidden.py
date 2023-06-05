from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Restricts the topdown_rule_index values according to the sequences in topdown forbidden constraints.
"""
def enforce_topdown_forbidden(dv: DecisionVariables):     
    return [
        any(
            path[tdf[i]] != path[tdf[i+1]]-1
            for i in range(len(tdf)-1)
        )
        for tdf in dv.g.TOPDOWN_FORBIDDEN
        for path in dv.topdown_rule_index        
    ]