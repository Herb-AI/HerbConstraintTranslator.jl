from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_topdown_ordered(dv: DecisionVariables):     
    sat_topdown_size = [
        # The last rule in the order should not occur if the rule path 
        # is not long enough to fit the entire rule order
         [
              [rule_path[r] != tdo[-1]]
              for tdo in dv.g.TOPDOWN_ORDERED
              for rule_path in dv.ancestor_rule 
              for r in range(0, len(tdo))
         ]
    ]
     
    sat_topdown = [
        # From where the rule path is long enough to contain the entire rule order, 
        # the last rule in the order doesn't occur, or the topdown ordering constraint 
        # needs to be satisfied. Meaning, the indexes stored for that constraint need 
        # to be in ascending order.
        [
            (Count(rule_path[len(tdo)-1:], tdo[-1]) == 0) 
            |   (
                    (dv.topdown_ordered[j, k] 
                    < dv.topdown_ordered[j, k+1]) 
                for k in range(dv.g.TDO_IDXS[i], dv.g.TDO_IDXS[i+1]-1)
                )
            for i, tdo in enumerate(dv.g.TOPDOWN_ORDERED) 
            for j, rule_path in enumerate(dv.ancestor_rule) 
            if len(tdo) < len(rule_path)
        ]
    ]
    
    if len(sat_topdown) == 0:
       return sat_topdown_size
     
    restrict_topdown = [
        # Restricts topdown_ordered decision variable according to ancestor_rule.
        [
            # Takes the minimum of all the indexes stored. If the rule wasn´t present in the path
            # this is max_depth+1, one bigger than any possible index. If it was present it takes
            # the lowest index where the rule was present.
            min(
                # Uses arithmetic to store the index of the value in rule_path that is 
                # the same as in the constraint, otherwise max_depth+1 is stored instead.
                # a.k.a. if the rule on the path is the same as the rule in the constraint
                # the equation leads to 0*(max_depth+1)+idx = idx, else it becomes equal or larger 
                # than max_depth+1, and due to the min it is then set to max_depth+1 which is
                # one bigger than the maximum real index.
                [
                    min([
                        dv.max_depth+1, 
                        abs( Element(rule_path, rule_idx)-tdo[order_idx] )*(dv.max_depth+1) + rule_idx
                    ]) for rule_idx in range(len(rule_path))
                ] +
                
                # Also enforces the rule for the current node, since ancestor_rule doesn't contain this.
                [
                    min([
                        dv.max_depth+1, 
                        abs( Element(dv.rule, path_idx)-tdo[order_idx] )*(dv.max_depth+1) + path_idx
                    ])
                ]
            ) == dv.topdown_ordered[path_idx, dv.g.TDO_IDXS[tdo_idx] + order_idx]
            for tdo_idx, tdo in enumerate(dv.g.TOPDOWN_ORDERED)
            for path_idx, rule_path in enumerate(dv.ancestor_rule)
            for order_idx in range(len(tdo))
        ]
    ]
     
    return restrict_topdown + sat_topdown + sat_topdown_size