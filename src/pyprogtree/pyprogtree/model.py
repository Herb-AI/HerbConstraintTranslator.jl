from cpmpy import Model, SolverLookup
from cpmpy.solvers import CPM_ortools

from pyprogtree.constraints import *
from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.match_node import MatchNode
from pyprogtree.plot_tree import plot_tree

def solve(g, min_n, max_n, max_depth=float("inf"), solution_limit=100):
    """
    Finds a feasible AST using global variables from 'csg_data.py', then plots it.
    :param g: grammar encoding
    :param min_n: minimum number of nodes in the tree
    :param max_n: maximum number of nodes in the tree
    :param max_depth: (optional) maximum depth of the tree
    :param solution_limit: maximum number of solution to create
    :return:
    """

    max_depth = min(max_n, max_depth)
    dv = DecisionVariables(g, min_n, max_n, max_depth)

    for rule in g.SUBTREE_ORDERED:
        rule[0].setup(dv)
        order = rule[1] # TODO: handle order
    
    for rule in g.SUBTREE_FORBIDDEN:
        rule[0].setup(dv)

    print("Setting up the model... ", end='')

    model = Model(
        enforce_tree(dv),
        enforce_child_index(dv),
        enforce_empty_nodes(dv),
        enforce_ancestor_path(dv),
        enforce_ancestor_rule(dv),
        enforce_first_ordering(dv),
        enforce_treesize(dv),
        enforce_spaceship(dv),
        enforce_topdown_rule_index(dv),
        enforce_leftright_rule_index(dv),
        enforce_topdown_ordered(dv),
        enforce_topdown_forbidden(dv),
        enforce_leftright_ordered(dv)
    )
    print("DONE")

    """
    #Examples of forbidden:
    node = MatchNode(dv, 6, children=[
        MatchNode(dv, 'x'),
        MatchNode(dv, 'x')
    ])
    model += constraint_forbidden(dv, node)

    node = MatchNode(dv, 2, children=[
        MatchNode(dv, 'x'),
        MatchNode(dv, 'y'),
        MatchNode(dv, 'z')
    ])
    model += constraint_forbidden(dv, node)

    # Example of ordered:
    node = MatchNode(dv, 8, children=[
        MatchNode(dv, 'x'),
        MatchNode(dv, 'y')
    ])
    model += constraint_ordered(dv, node, ['x', 'y'])

    # Fixed tree structure:
    model += (dv.rule[0] == dv.g.RULE_NAMES.index("4"))
    model += (dv.rule[1] == dv.g.RULE_NAMES.index("3"))
    model += (dv.rule[2] == dv.g.RULE_NAMES.index("/"))
    model += (dv.rule[3] == dv.g.RULE_NAMES.index("4"))
    model += (dv.rule[4] == dv.g.RULE_NAMES.index("Sqrt"))
    model += (dv.rule[5] == dv.g.RULE_NAMES.index(">="))
    model += (dv.rule[6] == dv.g.RULE_NAMES.index("F"))
    model += (dv.rule[7] == dv.g.RULE_NAMES.index("&&"))
    model += (dv.rule[8] == dv.g.RULE_NAMES.index("Not"))
    """
    
    def callback():
        dv.save_solution()
        print(f"\r{len(dv.solutions)}/{solution_limit} Solutions Found", end="")
        plot_tree(g, dv.parent, dv.rule,
                  show_types=False,
                  show_rules=True,
                  show_node_index=True,
                  show_empty_nodes=True,
                  show_lambda_string=lambda n: f"{''}")

    print(f"Solving the model... ")
    solver: CPM_ortools = SolverLookup.get(None, model)
    number_of_solutions = solver.solveAll(display=callback, solution_limit=solution_limit)
    print("")

    # print("PARENT:", dv.parent.value())
    # print("CHILD INDEX:", dv.child_index.value())
    # print("RULE: ", dv.rule.value())
    # print("TOPDOWN_RULE: ", dv.topdown_rule_index.value())
    # print("LEFTRIGHT_RULE: ", dv.leftright_rule_index.value())

    #dv.compare_solutions()
    
    print(f"Found {number_of_solutions} solutions")
    
    # Return and decision variables to reconstruct the full program tree
    return list(
        zip(map(lambda s: s['parent'][s['init_index']:] - s['init_index'], dv.solutions), 
            map(lambda s: s['rule'][s['init_index']:], dv.solutions))
    )

