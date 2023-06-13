from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Restricts the ancestor rule and rule decision variables according to the topdown forbidden
constraints.

The first constraint group restricts the rules in ancestor_rule to forbid the topdown forbidden
constraints.

The second constraint group restricts the rules in the ancestor_rule and the rule decision variable
to forbid the topdown forbidden constraints. This is necessary since the terminal node is not 
included in ancestor_rule.
"""
def enforce_topdown_forbidden(dv: DecisionVariables):     
    return [
        [
            any(
                path[start+tdf_range] != tdf[tdf_range] 
                for tdf_range in range(len(tdf))
            )

            for tdf in dv.g.TOPDOWN_FORBIDDEN
            for path in dv.ancestor_rule
            for start in range(len(path)-len(tdf))
        ], 
        [
            any(
                [
                    path[Element(dv.depth, n)-len(tdf)+1 + tdf_idx] != tdf[tdf_idx] 
                    for tdf_idx in range(len(tdf)-1)
                ]+[ dv.rule[n] != tdf[-1] ]
            )

            for tdf in dv.g.TOPDOWN_FORBIDDEN
            for n, path in enumerate(dv.ancestor_rule)
        ]
    ]