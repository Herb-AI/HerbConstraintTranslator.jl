from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_topdown_forbidden(dv: DecisionVariables):     
    return [
        [
            # Forbids the path from occurring in the paths of ancestor_rule.
            any(
                rule_path[i+r] != tdf[r]
                for r in range(len(tdf))
            )
            for rule_path in dv.ancestor_rule
            for tdf in dv.g.TOPDOWN_FORBIDDEN
            if len(rule_path) > len(tdf)
            for i in range(0, len(rule_path)-len(tdf)+1)
        ],
            # Forbids the path from occurring ending in terminal nodes, as these do not exist in ancestor_rule.
        [
            any(
                [
                    rule_path[len(rule_path)-len(tdf)+1+r] != tdf[r]
                    for r in range(len(tdf)-1)
                ]+[
                    dv.rule[node_of_path] != tdf[-1]
                ]
            )
            for node_of_path, rule_path in enumerate(dv.ancestor_rule)
            for tdf in dv.g.TOPDOWN_FORBIDDEN
            if len(rule_path) > len(tdf)
        ],
    ]