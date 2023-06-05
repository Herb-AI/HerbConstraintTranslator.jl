from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Restricts the leftright_rule decision variable according to rule.

It retrieves the index by using the equation:
    outcome = abs(<actual_rule> - <wanted_rule>) * max_n+1 + <index_actual_rule>
It does this for every position in rule, and takes the minimum of all of these and max_depth+1,
to get the minimum index of the <wanted_rule> in rule.

This is what leftright_rule[<wanted_rule>] is restricted to. 

max_n+1 is used as the maximum value, since it is one bigger than the possible value.
"""    
def enforce_leftright_rule(dv: DecisionVariables): 
    return [
        min([
                dv.max_n+1
            ] + abs( dv.rule[n] - r )*(dv.max_n+1) + n
                for n in range(dv.max_n)

            ) == dv.leftright_rule[r]
        for r in range(dv.g.NUMBER_OF_RULES)
    ]