from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Retricts the topdown_rule_index values in two ways:
    1. The index at which a rule occurs, needs to be great enough to fit the entire order 
        coming before.
    2. From where the rule path is long enough to contain the entire rule order, the last rule
        in the order doesn't occur, or the indexes corresponding to the rules in the constraint 
        need to be in strictly ascending order.
"""
def enforce_topdown_ordered(dv: DecisionVariables): 
    first = [
        (dv.rule[x] != sequence[-1])

        for sequence in dv.g.TOPDOWN_FORBIDDEN
        if len(sequence) > dv.max_depth
        for x in range(dv.max_n)
    ]

    second = [
         (Count([path] + [dv.rule[n]], sequence[-1]) >= 1).implies(
                all([
                        Count(path[a:b], transition[c]) > repetition[c]-1 for a,b,c in zippy[:-1]
                    ]+[
                        (Count([path[a:b]] + [dv.rule[n]], transition[c]) > repetition[c]-1) for a,b,c in zippy[-1:]
                    ])                       
            )
            for sequence, path, n, transition, repetition, zippy in topdown_helper(dv)]
    
    return first + second


def topdown_helper(dv):
     for sequence in dv.g.TOPDOWN_ORDERED:
        if len(sequence) <= dv.max_depth:
            repetition, transition = make_helpers(sequence)
            for n, path in enumerate(dv.ancestor_rule):
                for index_set in make_loopies(len(repetition)-1, 1,len(path)):
                    zippy = list(zip(index_set[:-1],index_set[1:], range(len(transition))))
                    yield sequence, path, n, transition, repetition, zippy

def make_loopies(vars, start, depth, acc=[0]):
	if vars == 0:
		yield acc+[depth]
		return
	for i in range(start+1, depth):
		yield from make_loopies(vars - 1, i, depth, acc + [ i ])
                
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