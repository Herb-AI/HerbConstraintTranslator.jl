from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_leftright_rule_indexes(dv: DecisionVariables):
    constraints = []

    for n in range(dv.max_n):
        for r in dv.g.LEFTRIGHT_REPEATS:
            constraints.append((dv.rule[n] != r))

    for r, repeats in enumerate(dv.g.LEFTRIGHT_DIMENSIONS):
        for occurence in range(repeats):
            if r in dv.g.LEFTRIGHT_REPEATS:
                constraints.append(all(dv.leftright_rule_indexes[r] == -1))
                break

            if occurence == 0:
                constraints.append((
                        max(
                            [
                                -1
                            ]+[
                                abs(dv.rule[n] - r) * (-1*dv.max_n) + n
                                for n in range(dv.max_n)
                            ]
                            )
                    == dv.leftright_rule_indexes[r][occurence])
                )
            else:
                constraints.append((dv.leftright_rule_indexes[r][occurence-1] != -1) | (dv.leftright_rule_indexes[r][occurence] == -1))
                constraints.extend(
                    [((n != (dv.leftright_rule_indexes[r][occurence-1]+1)) | (
                        max([
                                -1
                                ]+[ 
                                abs(dv.rule[n2] - r) * (-1*dv.max_n) + dv.depth[n2] for n2 in range(n)
                            ]) == dv.leftright_rule_indexes[r][occurence]
                    ))
                    for n in range(dv.max_n-occurence)]
                )

    return constraints

