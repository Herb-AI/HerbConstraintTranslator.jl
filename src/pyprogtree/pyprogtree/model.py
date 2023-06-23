from time import sleep

from cpmpy import Model, SolverLookup
from cpmpy.solvers import CPM_ortools

from pyprogtree.constraints import *
from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.plot_tree import plot_tree

def solve(g, min_n, max_n, max_depth=float("inf"), solution_limit=100, plot_solutions=True):
    """
    Finds a feasible AST using global variables from 'csg_data.py', then plots it.
    :param g: grammar encoding
    :param min_n: minimum number of nodes in the tree
    :param max_n: maximum number of nodes in the tree
    :param max_depth: (optional) maximum depth of the tree
    :param solution_limit: maximum number of solution to create
    :return:
    """
    if return_type != None:
        return_type -= 1
        assert 0 <= return_type < len(g.TYPE_NAMES), "Return type out of bounds!"

    max_depth = min(max_n, max_depth)
    dv = DecisionVariables(g, min_n, max_n, max_depth, return_type)

    #print("Setting up the model... ", end='')

    model = Model(
        enforce_tree(dv),
        enforce_child_index(dv),
        enforce_empty_nodes(dv),
        enforce_ancestor_path(dv),
        enforce_ancestor_rule(dv),
        enforce_first_ordering(dv),
        enforce_treesize(dv),
        enforce_spaceship(dv),
        enforce_topdown_ordered(dv),
        enforce_topdown_forbidden(dv),
        enforce_leftright_ordered(dv),
        enforce_subtree_forbidden(dv),
        enforce_subtree_ordered(dv),
        #enforce_implied_constraints(dv)
    )
    #print("DONE")

    # # Fixed tree structure:
    # model += (dv.rule[9] == dv.g.RULE_NAMES.index("?"))
    # model += (dv.rule[8] == dv.g.RULE_NAMES.index("Not"))
    # model += (dv.rule[7] == dv.g.RULE_NAMES.index("F"))
    # model += (dv.rule[6] == dv.g.RULE_NAMES.index("3"))
    # model += (dv.rule[5] == dv.g.RULE_NAMES.index("Sqrt"))
    # model += (dv.rule[4] == dv.g.RULE_NAMES.index("Sqrt"))
    # model += (dv.rule[3] == dv.g.RULE_NAMES.index("?"))
    # model += (dv.rule[2] == dv.g.RULE_NAMES.index("T"))
    # model += (dv.rule[1] == dv.g.RULE_NAMES.index("4"))
    # model += (dv.rule[0] == dv.g.RULE_NAMES.index("4"))
    #
    # Manual forbidden
    # node = MatchNode(2, children=[MatchNode(8), MatchNode(1), MatchNode(1)], fixed_index=3)
    # node.setup(dv)
    # model += constraint_local_forbidden(dv,node)
    
    def callback():
        dv.save_solution()
        if plot_solutions:
            print(f"\r{len(dv.solutions)}/{solution_limit} Solutions Found", end="")
            plot_tree(g, dv.parent, dv.rule,
                    save_fig=False,
                    show_types=False,
                    show_rules=True,
                    show_node_index=True,
                    show_empty_nodes=True,
                    show_lambda_string=lambda n: f"{dv.child_index[n].value()}")

    #print(f"Solving the model... ")
    solver: CPM_ortools = SolverLookup.get(None, model)
    number_of_solutions = solver.solveAll(display=callback, solution_limit=solution_limit)
    #print("")

    # print("PARENT:", dv.parent.value())
    # print("CHILD INDEX:", dv.child_index.value())
    # print("RULE: ", dv.rule.value())
    # print("TOPDOWN_RULE: ", dv.topdown_rule_index.value())
    # print("LEFTRIGHT_RULE: ", dv.leftright_rule_index.value())

    #dv.compare_solutions()

    # print(node.children[2]._location_exists().value())
    # print(node.children[2].child_index)
    # print(node.children[2].parent)
    # print("-----")
    # print(dv.child_index[0].value())
    # print(dv.parent[0].value())
    
    print(f"Found {number_of_solutions} solutions")
    
    # Return and decision variables to reconstruct the full program tree
    return list(
        zip(map(lambda s: s['parent'][s['init_index']:] - s['init_index'], dv.solutions), 
            map(lambda s: s['rule'][s['init_index']:], dv.solutions))
    )

