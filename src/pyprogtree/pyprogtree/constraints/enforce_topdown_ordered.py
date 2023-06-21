from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Enforces the topdown ordered constraint in three ways:
    1. It restricts the values in decision variable rule from having the value of the last
       in the sequence, if the sequence is larger than the amount of nodes.
    2. If the last value in the sequence occurs at least once on the path to the node, combined
       with the rule of the node itself, this implies the other rules in the sequence need to also
       occur the required amount of times (repeats). The last range also includes the rule the node
       the path leads to.
    3. The root cannot be the last in a sequence. This needs to be added, since the code relies on
       every path being checked, and that of the root is not in ancestor_rule. This addition
       remedies that difference.
"""
def enforce_topdown_ordered(dv: DecisionVariables): 
    return [
          
        (dv.rule[n] != sequence[-1])

        for sequence in dv.g.TOPDOWN_FORBIDDEN
        if len(sequence) > dv.max_depth
        for n in range(dv.max_n)
    ] + [
        any([
            (Count([path] + [dv.rule[n]], sequence[-1]) >= 1).implies(
            
                    all([
                        (Count(path[a:b], transition[c]) > repetition[c]-1) 
                        if c != (len(transition)-1)
                        else (Count([path[a:b]] + [dv.rule[n]], transition[c]) > repetition[c]-1) 
                        for a,b,c in list(zip(index_set[:-1],index_set[1:], range(len(transition))))
                    ])  
                )
            for index_set in range_permutations(len(repetition)-1, 0, len(path))
        ]) 
        for sequence in dv.g.TOPDOWN_ORDERED
        if len(sequence) <= dv.max_depth
        for repetition, transition in [make_helpers(sequence)]
        for n, path in enumerate(dv.ancestor_rule)
            
    ] + [
        dv.rule[dv.max_n-1] != sequence[-1]
        for sequence in dv.g.TOPDOWN_ORDERED
    ]


def range_permutations(vars, start, depth, acc=[0]):
    if vars == 0:
        yield acc+[depth]
        return
    for i in range(start+1, depth):
        yield from range_permutations(vars - 1, i, depth, acc + [ i ])
                
def make_helpers(sequence):
    transitions = [sequence[0]]
    repetitions = []
    last = sequence[0]
    count = 0

    for i in sequence:
        if i != last:
            repetitions.append(count)
            count = 1
            transitions.append(i)
            last = i
        else:
            count += 1
    repetitions.append(count)
    print(f"sequence: {sequence}")
    print(f"repetitions: {repetitions}")
    print(f"transitions: {transitions}")
    return repetitions, transitions      