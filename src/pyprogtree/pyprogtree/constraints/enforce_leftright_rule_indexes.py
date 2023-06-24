from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
The decision variable leftright_rule_indexes is enforced using 5 constraints:
    1. Repeats in sequences are forbidden from ever being selected as a rule in the rule dv.
    2. Repeats in the sequences therefore always have index -1 in leftright_rule_indexes
    3. The first occurrence of a rule has the highest index where it occurs in the entire range
       of the rule dv.
    4. Later indexes of occurrences are set to -1, if the previous occurrence was also -1.
    5. Later occurrences start checking the indexes from where their predecessor occurred.
"""
def enforce_leftright_rule_indexes(dv: DecisionVariables):
    return [
        (dv.rule[node] != rule)
        for node in range(dv.max_n)
        for rule in dv.g.LEFTRIGHT_REPEATS
    ] + [
        all(dv.leftright_rule_indexes[rule] == -1)
        for rule in range(len(dv.g.LEFTRIGHT_DIMENSIONS))
        if rule in dv.g.LEFTRIGHT_REPEATS
    ] + [
        (max([-1] + [abs(dv.rule[node] - rule) * (-1*dv.max_n) + node for node in range(dv.max_n)]) 
         == dv.leftright_rule_indexes[rule][0])
        for rule, repeats in enumerate(dv.g.LEFTRIGHT_DIMENSIONS)
        if repeats > 0
    ] + [
        ((dv.leftright_rule_indexes[rule][occurrence-1] != -1) | (dv.leftright_rule_indexes[rule][occurrence] == -1))
        for rule, repeats in enumerate(dv.g.LEFTRIGHT_DIMENSIONS)
        for occurrence in range(1,repeats)
    ] + [
        ((node != dv.leftright_rule_indexes[rule][occurrence-1]+1) | 
         (max([-1] + [abs(dv.rule[node2] - rule) * (-1*dv.max_n) + node2 for node2 in range(node)])))
        for rule, repeats in enumerate(dv.g.LEFTRIGHT_DIMENSIONS)
        for occurrence in range(1,repeats)
        for node in range(dv.max_n - occurrence)
    ]