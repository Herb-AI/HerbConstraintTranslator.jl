from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
The decision variable leftright_rule_indexes is enforced using 5 constraints:
    1. Repeats in sequences are forbidden from ever being selected as a rule in the rule dv.
    2. Repeats in the sequences therefore always have index -1 in leftright_rule_indexes
    3. The first occurrence of a rule has the highest index where it occurs in the entire range
       of the rule dv.
"""
def enforce_leftright_rule_indexes(dv: DecisionVariables):
    return [
        (dv.rule[n] != rule)

        for n in range(dv.max_n)
        for rule in dv.g.LEFTRIGHT_REPEATS

    ] + [
        (dv.leftright_rule_indexes[rule] == -1)

        for rule, repeats in enumerate(dv.g.LEFTRIGHT_DIMENSIONS)
        if  repeats > 0 and rule in dv.g.LEFTRIGHT_REPEATS

    ] + [
        max([-1
            ]+[
            abs(dv.rule[n] - rule) * (-1*dv.max_n) + n 
            for n in range(dv.max_n)
            ]) == dv.leftright_rule_indexes[rule]

        for rule, repeats in enumerate(dv.g.LEFTRIGHT_DIMENSIONS)
        if  repeats > 0

    ] 