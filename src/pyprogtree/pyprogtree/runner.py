from pyprogtree.grammar import *
from pyprogtree.model import *

def run(ruletypes, childtypes, typenames, rulenames, constraints):
    # Convert input ndarrays to python lists
    ruletypes  = list(ruletypes)
    childtypes = list(map(list, childtypes))
    typenames  = list(typenames)
    rulenames  = list(rulenames)
    constraints = list(constraints)
    # Create a grammar from rules:
    g = Grammar(ruletypes, childtypes, typenames, rulenames, constraints)
    # Find a solution:
    parent, rule = solve(g, 15, 15, max_depth=4)
    
    return parent, rule

if __name__ == "__main__":
    ruletypes  = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1]
    childtypes = [[], [], [1, 0, 0], [0], [1], [1, 1], [0, 0], [0, 0], [], []]
    typenames  = ['Real', 'Bool']
    rulenames  = ['3', '4', '?', 'Sqrt', 'Not', '&&', '+', '>=', 'T', 'F']
    constraints = []
    run(ruletypes, childtypes, typenames, rulenames, constraints)

"""
The test grammar:
[
    ["3", "Real", []],
    ["4", "Real", []],
    ["?", "Real", ["Bool", "Real", "Real"]],
    ["Sqrt", "Real", ["Real"]],
    ["Not", "Bool", ["Bool"]],
    ["&&", "Bool", ["Bool", "Bool"]],
    ["+", "Real", ["Real", "Real"]],
    [">=", "Bool", ["Real", "Real"]],
    ["T", "Bool", []],
    ["F", "Bool", []]
]
"""