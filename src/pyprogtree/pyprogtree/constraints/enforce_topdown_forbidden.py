from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.constraints.enforce_topdown_ordered import range_permutations, make_helpers 
from cpmpy import *

"""
Enforces the topdown forbidden constraint. It generates all the ranges the ancestor_rule array could
be divided into, and checks if for all these ranges, at least one of the constraints holds. These
constraints state there is less than the repeats in the sequence of this rule, in this sequence. 
"""
def enforce_topdown_forbidden(dv: DecisionVariables):   
    return [
         any([
               (Count(path[a:b], transition[c]) < repetition[c]) if c < (len(transition)-1)
               else (Count([path[a:b]] + [dv.rule[n]], transition[c]) < repetition[c])
                 
               for a,b,c in list(zip(index_set[:-1],index_set[1:], range(len(transition))))
            ])
                for sequence in dv.g.TOPDOWN_FORBIDDEN
                if len(sequence) <= dv.max_depth
                for repetition, transition in [make_helpers(sequence)]
                for n, path in enumerate(dv.ancestor_rule)
                for index_set in range_permutations(len(repetition)-1, 0, len(path))
    ]