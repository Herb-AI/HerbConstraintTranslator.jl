from src.pyprogtree.decision_variables import DecisionVariables
from cpmpy import *

def enforce_leftright_ordered(dv: DecisionVariables):     
    return [
        # The kth rule in the sequence should not occur if there are
        # not k nodes before to fit the entire sequence.
         [
              [dv.rule[n] != lro[r]]
              for lro in dv.g.LEFTRIGHT_ORDERED
              for n in range(dv.max_n-len(lro)+1, dv.max_n) 
              if dv.max_n-n < len(lro)
              for r in range(dv.max_n-n, len(lro))
         ],

        # For every leftright constraint, the kth index should be less than the
        # k+1th index for that rule.
        [
            (dv.leftright_ordered[lro[r]] 
            <= dv.leftright_ordered[lro[r+1]]) 

            for lro in dv.g.LEFTRIGHT_ORDERED
            for r in range(len(lro)-1)
        ],

        # Restricts the leftright_ordered decision variable according to rule.
        [
                # Uses arithmetic to constrain the index x of leftright_ordered to be the lowest
                # index in the rule decision variable where rule x occurs, if it doesn't occur
                # max_n+1 is stored instead.
            min(
                # If it occurs, the equation leads to 0*(max_n+1)+idx = idx, 
                # else it becomes equal or larger than max_n+1.
                [
                    min([
                        dv.max_n+1, 
                        abs( dv.rule[n]-r )*(dv.max_n+1) + n
                    ]) for n in range(dv.max_n)
                ]
            ) == dv.leftright_ordered[r]
            for r in range(dv.g.NUMBER_OF_RULES)
        ]
    ]