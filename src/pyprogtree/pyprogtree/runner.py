from pyprogtree.grammar import *
from pyprogtree.model import *

def run(ruletypes, childtypes, typenames, rulenames):
    # Create a grammar from rules:
    g = Grammar(ruletypes, childtypes, typenames, rulenames)
    # Find a solution:
    solve(g, 15, 15, max_depth=4)
    # TODO: decode the resulting program
"""
if __name__ == "__main__":
    run([
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
    ])
"""