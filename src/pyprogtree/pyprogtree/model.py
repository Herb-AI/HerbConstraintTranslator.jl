from cpmpy import Model
from pyprogtree.constraints import *
from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.match_node import MatchNode
from pyprogtree.plot_tree import plot_tree

def solve(g, min_n, max_n, max_depth=float("inf")):
    """
    Finds a feasible AST using global variables from 'csg_data.py', then plots it.
    :param g: grammar encoding
    :param min_n: minimum number of nodes in the tree
    :param max_n: maximum number of nodes in the tree
    :param max_depth: (optional) maximum depth of the tree
    :return:
    """

    max_depth = min(max_n, max_depth)
    dv = DecisionVariables(g, min_n, max_n, max_depth)

    print("Setting up the model... ", end='')

    model = Model(
        enforce_tree(dv),
        enforce_child_index(dv),
        enforce_empty_nodes(dv),
        enforce_ancestor_path(dv),
        enforce_ancestor_rule(dv),
        enforce_first_ordering(dv),
        enforce_treesize(dv),
        enforce_spaceship(dv)
    )
    print("DONE")

    node = MatchNode(dv, 6, children=[
        MatchNode(dv, 'x'),
        MatchNode(dv, 'x')
    ], fixed_index=14)

    model += (node.enforce()) & (node.matched() == True)

    # todo: bug node.matched() doesn't work for MatchVars
    # node = MatchNode(dv, 6, children=[
    #     MatchNode(dv, 'x'),
    #     MatchNode(dv, 'x')
    # ], fixed_index=0)
    #
    # model += (node.enforce()) & (node.matched() == False)

    # Solving
    print("Solving the model... ", end='')
    is_optimal = model.solve()
    print("DONE")
    print(model.status())
    if is_optimal:
        plot_tree(g, dv.parent, dv.rule,
                  show_types=False,
                  show_rules=True,
                  show_node_index=True,
                  show_empty_nodes=True,
                  show_lambda_string=lambda n: f"{''}")

        print(dv.ancestor_path.value())
        print("DEPTH:", dv.depth.value())
        print("PARENT:", dv.parent.value())
        print("CHILD INDEX:", dv.child_index.value())

    return is_optimal