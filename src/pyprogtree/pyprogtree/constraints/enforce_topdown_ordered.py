from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Enforces the topdown ordered constraint in three ways:
    1. It restricts the values in decision variable rule from having the value of the last
       in the sequence, if the sequence is larger than the amount of nodes.
    2. If the last value in the sequence occurs at least once on the path to the node, combined
       with the rule of the node itself, this implies the other rules in the sequence need to also
       occur the required amount of times (repeats). The last range also includes the rule the node
       the path leads to.
    3. The root cannot be the last in a sequence. This needs to be added, since the code relies on
       every path being checked, and that of the root is not in ancestor_rule. This addition
       remedies that difference.
"""
def enforce_topdown_ordered(dv: DecisionVariables): 
    constraints = []
    for n in range(dv.max_n-1):
        for indexing, sequence in dv.g.TOPDOWN_ORDERED:
            constraints.append(
                ((dv.topdown_rule_indexes[n][sequence[-1]][0] == (dv.max_depth+1)) |
                 all(
                    [(dv.topdown_rule_indexes[n][sequence[i]][indexing[i]] < dv.topdown_rule_indexes[n][sequence[i+1]][indexing[i+1]]) for i in range(len(sequence)-1)]
                )))
            
    return constraints