from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_topdown_rule_indexes(dv: DecisionVariables):
    constraints = []
    for n, path in enumerate(dv.ancestor_rule):
        for r, repeats in enumerate(dv.g.TOPDOWN_DIMENSIONS):
            for occurence in range(repeats):
                if occurence == 0:
                    constraints.append((
                            min([   
                                dv.max_depth+1, 
                                abs(dv.rule[n] - r) * (dv.max_depth+1) + dv.depth[n]
                            ]+[
                                ((abs(path[d] - r) * (dv.max_depth+1) + d)) for d in range(dv.max_depth)
                            ]) 
                        == dv.topdown_rule_indexes[n][r][occurence])
                    )
                else:
                    constraints.extend( # TODO try without implies
                        [(d == (dv.topdown_rule_indexes[n][r][occurence-1]+1)).implies((
                            min([   
                                    dv.max_depth+1, 
                                    abs(dv.rule[n] - r) * (dv.max_depth+1) + dv.depth[n]
                                ]+[
                                    ((abs(path[d2] - r) * (dv.max_depth+1) + d2)) for d2 in range(d)
                                ]) == dv.topdown_rule_indexes[n][r][occurence]
                        ))
                        for d in range(dv.max_depth)]
                    )

    print(f"constraints index: {constraints}\n\n\n")
    return constraints

