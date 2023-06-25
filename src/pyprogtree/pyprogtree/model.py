from time import sleep, time

from cpmpy import Model, SolverLookup
from cpmpy.solvers import CPM_ortools

from pyprogtree.constraints import *
from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.plot_tree import plot_tree

def solve(g, min_n, max_n, max_depth=None, return_type=None, solution_limit=100, plot_solutions=True):
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
        enforce_topdown_rule_indexes(dv),
        enforce_topdown_ordered(dv),
        enforce_topdown_forbidden(dv),
        enforce_leftright_rule_indexes(dv),
        enforce_leftright_ordered(dv),
        enforce_subtree_forbidden(dv),
        enforce_subtree_ordered(dv),
        #enforce_implied_constraints(dv)
    )

    # Begin timing of the search:
    time_measurements = [time()]
    search_timing = []
    # time measurements => [s, t0, t1, t2]
    # search timing     => [t0 - s, t1 - t0, t2 - t1]
    
    def callback():
        # Record and save the elapsed time:
        last_time_id = len(time_measurements) - 1
        current_time = time()
        time_measurements.append(current_time)
        search_timing.append(current_time - time_measurements[last_time_id])

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
    start_time = time()
    
    if return_type == None:
        # make a separate model per return type
        model_real = model
        model_bool = model.copy()

        # run solver with Real as the return type
        model_real += enforce_return_type(dv, 0)
        solver: CPM_ortools = SolverLookup.get(None, model_real)
        real_solutions = solver.solveAll(display=callback, solution_limit=solution_limit, preferred_variable_order=1)
        # run solver with Bool as the return type
        model_bool += enforce_return_type(dv, 1)
        solver: CPM_ortools = SolverLookup.get(None, model_bool)
        bool_solutions = solver.solveAll(display=callback, solution_limit=solution_limit, preferred_variable_order=1)
        
        number_of_solutions = real_solutions + bool_solutions
    else:
        model += enforce_return_type(dv, return_type)
        solver: CPM_ortools = SolverLookup.get(None, model)
        number_of_solutions = solver.solveAll(display=callback, solution_limit=solution_limit, preferred_variable_order=1)
    
    end_time = time()
    
    print(f"Found {number_of_solutions} solutions")

    # Process the recorder timings:
    total_time = end_time - start_time
    print("Total time elapsed: ", total_time)
    print("Total sum of measurements: ", sum(search_timing))
    
    # Return and decision variables to reconstruct the full program tree
    return list(
        zip(map(lambda s: s['parent'][s['init_index']:] - s['init_index'], dv.solutions), 
            map(lambda s: s['rule'][s['init_index']:], dv.solutions))
    ), search_timing, total_time