from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Restricts the topdown_rule_index decision variable according to ancestor_rule.

It retrieves the index by using the equation:
    outcome = abs(<actual_rule> - <wanted_rule>) * max_depth+1 + <index_actual_rule>
It does this for every position on a path from ancestor_rule, and takes the minimum of all of
these and max_depth+1, to get the minimum index of the <wanted_rule> on this path.

This is what topdown_rule_index[path, <wanted_rule>] is restricted to. 

max_depth+1 is used as the maximum value, since it is one bigger than the possible value.
"""
def enforce_topdown_rule_index(dv: DecisionVariables): 
    return [
        min([
                 dv.max_depth+1,
                 abs( dv.rule[n]           -wanted_rule )*(dv.max_depth+1) + dv.depth[n] # This is added for terminal nodes. Could add | rule_path == -1, if it is a lazy evaluator?
            ] + [abs( dv.ancestor_rule[n,d]-wanted_rule )*(dv.max_depth+1) + d
                for d in range(dv.max_depth)]

            ) == dv.topdown_rule_index[n, wanted_rule]
        for n in range(dv.max_n-1)
        for wanted_rule in range(dv.g.NUMBER_OF_RULES)
    ]