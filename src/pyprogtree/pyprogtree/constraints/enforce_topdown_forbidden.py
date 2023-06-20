from pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

"""
Restricts the ancestor rule and rule decision variables according to the topdown forbidden
constraints.

The first constraint group restricts the rules in ancestor_rule to forbid the topdown forbidden
constraints.

The second constraint group restricts the rules in the ancestor_rule and the rule decision variable
to forbid the topdown forbidden constraints. This is necessary since the terminal node is not 
included in ancestor_rule.
"""
def enforce_topdown_forbidden(dv: DecisionVariables):     
    constraints = []
    for sequence in dv.g.TOPDOWN_FORBIDDEN:
        if len(sequence) > dv.max_depth:
            for x in range(dv.max_n):
                 constraints.append(dv.rule[x] != sequence[-1])
            continue
        repetition, transition = make_helpers(sequence)

        for n, path in enumerate(dv.ancestor_rule):
             for index_set in make_loopies(len(repetition)-1, 1, len(path)):
                  zippy = list(zip(index_set[:-1],index_set[1:], range(len(transition))))
                  print(zippy)
                  constraints.append(
                       any(
                      [(Count(path[a:b], transition[c]) < repetition[c]) for a,b,c in zippy[:-1]]+ [
                            (Count([path[a:b]] + [dv.rule[n]], transition[c]) < repetition[c]) for a,b,c in zippy[-1:]
                        ])
                  )
    return constraints

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