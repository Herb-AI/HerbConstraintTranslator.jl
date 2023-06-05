from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_topdown_ordered(dv: DecisionVariables): 
    """
    Restricts topdown_ordered decision variable according to ancestor_rule.

    It retrieves the index by using the equation:
        outcome = abs(<actual_rule> - <wanted_rule>) * <max_depth+1> + <index_actual_rule>
    It does this for every position on a path from ancestor_rule, and takes the minimum of all of
    these and max_depth+1, to get the minimum index of the <wanted_rule> on this path.
    
    This is what topdown_ordered[path, <wanted_rule>] is restricted to. 

    max_depth+1 is used as the maximum value, since it is one bigger than the possible value.
    """
    # Should the max be max_depth+2? since I saw that terminal nodes are not in ancestor_rule,
    # and it ranges till max_depth, so terminal nodes could be max_depth+1 I think...
    restrict_topdown = [
        [
            min(
                [
                    dv.max_depth+1,
                    abs( dv.rule[n]      -rule_value )*(dv.max_depth+1) + dv.depth[n] # This is added for terminal nodes. Could add | rule_path == -1, if it is a lazy evaluator?
                ] + 
                    abs( rule_path[depth]-rule_value )*(dv.max_depth+1) + depth
                    for depth in range(len(rule_path))

            ) == dv.topdown_ordered[n, rule_value]
            for n, rule_path in enumerate(dv.ancestor_rule)
            for rule_value in range(dv.g.NUMBER_OF_RULES)
        ]
    ]
   
    """
    The index at which a rule occurs, needs to be great enough to fit the entire order coming
    before.
    """
    sat_topdown_size = [
        [
            dv.topdown_ordered[n,r] > idx
            for tdo in enumerate(dv.g.TOPDOWN_ORDERED)
            for n in range(dv.max_n)
            for idx, r in enumerate(tdo[1:])
        ]
    ]

    """
    From where the rule path is long enough to contain the entire rule order, the last rule in the 
    order doesn't occur, or the topdown ordering constraint needs to be satisfied. Meaning, the 
    indexes corresponding to the rules in the constraint need to be in ascending order.
    """
    # Count could be removed if the operator is changed to <=
    sat_topdown = [
        [ 
            (Count(rule_path[len(tdo)-1:], tdo[-1]) == 0)  
            |   (
                    (dv.topdown_ordered[j, tdo[k]] 
                    < dv.topdown_ordered[j, tdo[k+1]]) 
                    for k in range(tdo-1)
                )
            for tdo in dv.g.TOPDOWN_ORDERED 
            for j, rule_path in enumerate(dv.ancestor_rule) 
            if len(tdo) < len(rule_path)
        ]
    ]
     
    return restrict_topdown + sat_topdown + sat_topdown_size