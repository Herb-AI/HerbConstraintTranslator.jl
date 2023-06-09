from pyprogtree.grammar import *
from pyprogtree.match_node import MatchNode
from pyprogtree.model import *
from pyprogtree.timeit import *

@timeit
def run(ruletypes, childtypes, typenames, rulenames, constraints, 
        min_nodes=1, max_nodes=3, max_depth=3, return_type=None, solution_limit=None, plot_solutions=False):
    # Convert input ndarrays to python lists
    ruletypes  = list(ruletypes)
    childtypes = list(map(list, childtypes))
    typenames  = list(typenames)
    rulenames  = list(rulenames)
    constraints = list(constraints)
    # Create a grammar from rules:
    g = Grammar(ruletypes, childtypes, typenames, rulenames, constraints)
    # Find a solution:
    return solve(g, min_nodes, max_nodes, max_depth, return_type, solution_limit, plot_solutions)

if __name__ == "__main__":
    ruletypes  = [0, 0, 0, 1, 1]
    childtypes = [[], [], [1, 0, 0], [], []]
    typenames  = ['Real', 'Bool']
    rulenames  = ['3', '4', '?', 'T', 'F']
    constraints = [
                #["TDF",[4,4]],
                ["TDO", [5,9]],
                #["LRO", [3,0]],
                #["O", [MatchNode(6, children=[MatchNode("x"), MatchNode("y")]), ["x", "y"]]],
                #["F", MatchNode(6, children=[MatchNode("x"), MatchNode("x")])]
    ]
    run(ruletypes, childtypes, typenames, rulenames, constraints)

"""
The test grammar:
    ruletypes  = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1]
    childtypes = [[], [], [1, 0, 0], [0], [1], [1, 1], [0, 0], [0, 0], [], []]
    typenames  = ['Real', 'Bool']
    rulenames  = ['3', '4', '?', 'Sqrt', 'Not', '&&', '+', '>=', 'T', 'F']
"""