from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *
import numpy as np

"""
Retricts the leftright_rule_index values in two ways:
    1. The kth rule in the sequence should not occur if there are not k nodes before to fit the
        entire sequence.
    2. For every leftright ordered constraint, the kth index should be less than the k+1th 
        index for that rule.
"""
def enforce_leftright_ordered(dv: DecisionVariables): 
    constraints = []
    for sequence in dv.g.LEFTRIGHT_ORDERED:
        # if len(sequence) > dv.max_n:
        #     for x in range(dv.max_n):
        #          constraints.append(dv.rule[x] != sequence[-1])
        #     continue
        # TODO when there is a repeat, invalidate all up until that point
        # TODO when the sequence is longer than the total number of nodes, invalidate up until that point

        for n in range(dv.max_n):
            if n == dv.max_n-1:
                constraints.append(all(dv.rule[n] != sequence[k] for k in range(1, len(sequence))))
            else:
                constraints.extend([(dv.rule[n] == sequence[k]).implies(
                     Count(dv.rule[n+1:], sequence[k-1]) >= 1
                ) for k in range(1, len(sequence))])

    return constraints



def make_loopies(vars, depth, acc=[0]):
	if vars == 0:
		yield acc+[depth]
		return
	for i in range(1, depth):
		yield from make_loopies(vars - 1, depth, acc + [ i ])
                
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
    return repetitions, transitions   