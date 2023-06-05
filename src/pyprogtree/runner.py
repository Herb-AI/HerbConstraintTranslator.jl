from src.pyprogtree.grammar import *
from src.pyprogtree.model import *

def run(rules, constraints):
    # Create a grammar from rules:
    g = Grammar(rules, constraints)
    # Find a solution:
    solve(g, 11, 11, max_depth=4)
    # TODO: decode the resulting program

if __name__ == "__main__":
    run([
        ["3", "Real", []],
        ["4", "Real", []],
        ["?", "Real", ["Bool", "Real", "Real"]],
        ["Sqrt", "Real", ["Real"]],
        ["Not", "Bool", ["Bool"]],
        ["&&", "Bool", ["Bool", "Bool"]],
        ["+", "Real", ["Real", "Real"]],
        ["/", "Real", ["Real", "Real"]],
        [">=", "Bool", ["Real", "Real"]],
        ["T", "Bool", []],
        ["F", "Bool", []]
    ],
    [
    #    ["LRO", [3,2]]
    ]
    )

# Test TopDown Ordered -> with and without:
# ["TDO", [2,3]]

# Test LeftRight Ordered -> with and without:
# ["LRO", [3,2]]

# Test Forbidden Path where 3 and True should never occur in the tree:
# ["TDF", [2,9]],
# ["TDF", [2,0]],
# ["TDF", [3,0]],
# ["TDF", [4,9]],
# ["TDF", [5,9]],
# ["TDF", [6,0]],
# ["TDF", [7,0]],
# ["TDF", [8,0]]
