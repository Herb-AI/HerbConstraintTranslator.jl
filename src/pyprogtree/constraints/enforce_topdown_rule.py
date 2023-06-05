from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Restricts the topdown_rule decision variable according to ancestor_rule.

It retrieves the index by using the equation:
    outcome = abs(<actual_rule> - <wanted_rule>) * max_depth+1 + <index_actual_rule>
It does this for every position on a path from ancestor_rule, and takes the minimum of all of
these and max_depth+1, to get the minimum index of the <wanted_rule> on this path.

This is what topdown_rule[path, <wanted_rule>] is restricted to. 

max_depth+1 is used as the maximum value, since it is one bigger than the possible value.
"""
# Should the max be max_depth+2? since I saw that terminal nodes are not in ancestor_rule,
# and it ranges till max_depth, so terminal nodes could be max_depth+1 I think...
def enforce_topdown_rule(dv: DecisionVariables): 
    return [
        min([
                dv.max_depth+1,
                abs( dv.rule[n]      -rule_value )*(dv.max_depth+1) + dv.depth[n] # This is added for terminal nodes. Could add | rule_path == -1, if it is a lazy evaluator?
            ] + abs( rule_path[depth]-rule_value )*(dv.max_depth+1) + depth
                for depth in range(len(rule_path))

            ) == dv.topdown_rule[n, rule_value]
        for n, rule_path in enumerate(dv.ancestor_rule)
        for rule_value in range(dv.g.NUMBER_OF_RULES)
    ]