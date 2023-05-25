from pyprogtree.grammar import *
from pyprogtree.model import * 

def run(rules):
    # Create a grammar from rules:
    g = Grammar(rules)
    # Find a solution:
    solve(g, 15, 15, max_depth=4)
    # TODO: decode the resulting program