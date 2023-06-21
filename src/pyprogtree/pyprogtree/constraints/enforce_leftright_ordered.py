from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *
import numpy as np

"""
Enforces the leftright order in two ways:
    1. The kth rule in the sequence should not occur if there are not k nodes before to fit the
       entire sequence.
    2. If the kth rule in the sequence occurs, all rules before it in the sequence must have 
       occurred earlier in the ordering. In this case the ordering makes it after it in the
       rule decision variable.
"""
def enforce_leftright_ordered(dv: DecisionVariables): 
    return [
         
         ([dv.rule[n] != sequence[too_long] for n in dv.max_n])
         for sequence in dv.g.LEFTRIGHT_ORDERED
         if len(sequence) > dv.max_n
         for too_long in sequence[dv.max_n:]

    ] + [
         all(dv.rule[dv.max_n-1] != sequence[k] for k in range(1, len(sequence)))
        for sequence in dv.g.LEFTRIGHT_ORDERED
    ] + [
         (dv.rule[n] == sequence[k]).implies (
            Count(dv.rule[n+1:], sequence[k-1]) >= 1
         )
         for sequence in dv.g.LEFTRIGHT_ORDERED
         for n in range(dv.max_n-1)
         for k in range(1, len(sequence))
    ]





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