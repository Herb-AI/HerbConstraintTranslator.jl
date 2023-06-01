from cpmpy import Model

from src.pyprogtree.constraints.depth_first_ordering import DepthFirstOrdering
from src.pyprogtree.constraints.is_tree import IsTree
from src.pyprogtree.constraints.set_ancestor_rule import SetAncestorRule
from src.pyprogtree.constraints.set_child_index import SetChildIndex
from src.pyprogtree.constraints.set_empty_nodes import SetEmptyNodes
from src.pyprogtree.constraints.set_spaceship import SetSpaceShip
from src.pyprogtree.constraints.set_treesize import SetTreeSize
from src.pyprogtree.decision_variables import DecisionVariables
from src.pyprogtree.plot_tree import plot_tree

def solve(g, min_n, max_n, max_depth=float("inf")):
    """
    Finds a feasible AST using global variables from 'csg_data.py', then plots it.
    :param g: grammar encoding
    :param min_n: minimum number of nodes in the tree
    :param max_n: maximum number of nodes in the tree
    :param max_depth: (optional) maximum depth of the tree
    :return:
    """

    max_depth = min(max_n, max_depth+1)
    dv = DecisionVariables(g, min_n, max_n, max_depth)
    model = Model(
        IsTree(dv),
        SetChildIndex(dv),
        SetEmptyNodes(dv),
        SetAncestorRule(dv),
        SetAncestorRule(dv),
        SetTreeSize(dv),
        SetSpaceShip(dv),
        DepthFirstOrdering(dv)
    )

    # Solving
    is_optimal = model.solve()
    print(model.status())
    if is_optimal:
        # plot_tree(g, dv.parent, dv.rule,
        #           show_types=False,
        #           show_rules=True,
        #           show_node_index=True,
        #           show_empty_nodes=True,
        #           show_lambda_string=lambda n: f"{''}")

        print(dv.ancestor_rule.value())
        print("DEPTH:", dv.depth.value())
        print("PARENT:", dv.parent.value())
        print("CHILD INDEX:", dv.child_index.value())

    return is_optimal
