from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_topdown_rule_indexes(dv: DecisionVariables):
    constraints = []

    for n in range(dv.max_n):
        for r in dv.g.TOPDOWN_REPEATS:
            constraints.append((dv.rule[n] != r))

    for n in range(dv.max_n - 1):
        for r, repeats in enumerate(dv.g.TOPDOWN_DIMENSIONS):
            for occurence in range(repeats):
                if r in dv.g.TOPDOWN_REPEATS:
                    constraints.append(all(dv.topdown_rule_indexes[n][r] == (dv.max_depth+1)))
                    break

                if occurence == 0:
                    constraints.append((
                            min([   
                                dv.max_depth+1,
                                abs(dv.rule[n] - r) * (dv.max_depth+1) + dv.depth[n]
                            ]+[
                                ((abs(dv.ancestor_rule[n,d] - r) * (dv.max_depth+1) + d)) for d in range(dv.max_depth)
                            ]) 
                        == dv.topdown_rule_indexes[n][r][occurence])
                    )
                else:
                    constraints.append((dv.topdown_rule_indexes[n][r][occurence-1]+1 < dv.max_depth) | (dv.topdown_rule_indexes[n][r][occurence] == dv.max_depth+1))
                    constraints.extend(
                        [((d != (dv.topdown_rule_indexes[n][r][occurence-1]+1)) | (
                            min([   
                                    dv.max_depth+1, 
                                    abs(dv.rule[n] - r) * (dv.max_depth+1) + dv.depth[n]
                                ]+[
                                    ((abs(dv.ancestor_rule[n,d2] - r) * (dv.max_depth+1) + d2)) for d2 in range(d, dv.max_depth)
                                ]) == dv.topdown_rule_indexes[n][r][occurence]
                        ))
                        for d in range(dv.max_depth)]
                    )

    return constraints

