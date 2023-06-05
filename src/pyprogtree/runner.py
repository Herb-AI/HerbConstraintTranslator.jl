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
        # ["TDO", [2,3]],
        # ["LRO", [2,3]],
        ["TDF", [2,9]],
        ["TDF", [2,0]],
        ["TDF", [3,0]],
        ["TDF", [4,9]],
        ["TDF", [5,9]],
        ["TDF", [6,0]],
        ["TDF", [7,0]],
        ["TDF", [8,0]]
    ]
    )


    # ComesAfter(rule: Int, predecessors: [Int])
    # ForbiddenPath(sequence: [Int])
    # OrderedPath(order: [Int])

    # Ordered(tree: AbstractMatchNode, order: [Symbol])
    # Forbidden(tree: AbstractMatchNode)
    # LocalOrdered(path: [Int], tree: AbstractMatchNode, order: [Symbol])
    # LocalForbidden(path: [Int], tree: AbstractMatchNode)
