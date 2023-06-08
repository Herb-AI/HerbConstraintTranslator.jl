from pyprogtree.grammar import *
from pyprogtree.model import *

def run(ruletypes, childtypes, typenames, rulenames):
    # Convert input ndarrays to python lists
    ruletypes  = list(ruletypes)
    childtypes = list(map(list, childtypes))
    typenames  = list(typenames)
    rulenames  = list(rulenames)
    # Create a grammar from rules:ex
    g = Grammar(ruletypes, childtypes, typenames, rulenames)
    print("grammar constructed!")
    print("ruletypes: ", g.TYPES)
    print("childtypes:", g.CHILD_TYPES)
    print("typenames: ", g.TYPE_NAMES)
    print("rulenames: ", g.RULE_NAMES)
    # Find a solution:
    solve(g, 15, 15, max_depth=4)
    
    #TODO: decode the resulting program

if __name__ == "__main__":
    ruletypes  = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1]
    childtypes = [[], [], [1, 0, 0], [0], [1], [1, 1], [0, 0], [0, 0], [], []]
    typenames  = ['Real', 'Bool']
    rulenames  = ['3', '4', '?', 'Sqrt', 'Not', '&&', '+', '>=', 'T', 'F']
    run(ruletypes, childtypes, typenames, rulenames)

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