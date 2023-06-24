from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
The decision variable topdown_rule_indexes is enforced using 5 constraints:
    1. Repeats in sequences are forbidden from ever being selected as a rule in the rule dv.
    2. Repeats in the sequences therefore always have index max_depth+1 in topdown_rule_indexes.
    3. The first occurrence of a rule has the highest index where it occurs in the entire range
       of the path in ancestor_rule, together with the terminal node in rule.
    4. Later indexes of occurrences are set to max_depth+1, if the previous occurrence was also max_depth+1.
    5. Later occurrences start checking the indexes until where their predecessor occurred.
"""
def enforce_topdown_rule_indexes(dv: DecisionVariables):
    return [
        (dv.rule[node] != rule)

        for node in range(dv.max_n)
        for rule in dv.g.TOPDOWN_REPEATS
    ] + [
        all(dv.topdown_rule_indexes[node][rule] == (dv.max_depth+1))

        for node in range(dv.max_n-1)
        for rule, repeats in enumerate(dv.g.TOPDOWN_DIMENSIONS)
        if repeats > 0 and rule in dv.g.TOPDOWN_REPEATS
    ] + [
        (min([
            dv.max_depth+1, 
            abs(dv.rule[node] - rule) * (dv.max_depth+1) + dv.depth[node]
            ]+[
            (abs(dv.ancestor_rule[node, depth] - rule) * (dv.max_depth+1) + depth) 
            for depth in range(dv.max_depth)
            ]) == dv.topdown_rule_indexes[node][rule][0])

        for node in range(dv.max_n - 1)
        for rule, repeats in enumerate(dv.g.TOPDOWN_DIMENSIONS)
        if rule not in dv.g.TOPDOWN_REPEATS and repeats > 0        
    ] + [
        (dv.topdown_rule_indexes[node][rule][occurence-1] + 1 < dv.max_depth    ) | 
        (dv.topdown_rule_indexes[node][rule][occurence  ]    == dv.max_depth + 1)

        for node in range(dv.max_n - 1)
        for rule, repeats in enumerate(dv.g.TOPDOWN_DIMENSIONS)
        for occurence in range(1, repeats)
    ] + [
        (
            (d != (dv.topdown_rule_indexes[n][r][occurence-1]+1)
             ) | (
            min([
                dv.max_depth+1, 
                abs(dv.rule[n] - r) * (dv.max_depth+1) + dv.depth[n]
                ]+[
                (abs(dv.ancestor_rule[n,d2] - r) * (dv.max_depth+1) + d2) 
                for d2 in range(d, dv.max_depth)
                ]) == dv.topdown_rule_indexes[n][r][occurence])
        )
        for n in range(dv.max_n - 1)
        for r, repeats in enumerate(dv.g.TOPDOWN_DIMENSIONS)
        for occurence in range(1, repeats)
        for d in range(occurence, dv.max_depth)
    ]