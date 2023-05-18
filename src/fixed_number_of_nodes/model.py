from math import log, ceil
from cpmpy import intvar, Model
from cpmpy.expressions.globalconstraints import Element, Count
from plot_tree import plot_tree
from csg_data import *

def solve(min_n, max_n, max_depth=float("inf")):
    """
    Finds a feasible AST using global variables from 'csg_data.py', then plots it.
    :param min_n: minimum number of nodes in the tree
    :param max_n: maximum number of nodes in the tree
    :param max_depth: (optional) maximum depth of the tree
    :return:
    """

    # Todo: export fields from the (julia) csg struct to a python class that holds:
    #    * TYPES
    #    * CHILD_TYPES (flatted into a 1D array of size NUMBER_OF_RULES*MAX_ARITY)
    #    * TYPE_NAMES
    #    * RULE_NAMES
    #    * Processed fields:
    #        * a newly added "empty rule", for the cpmpy encoding
    #        * (implied) RULE_ARITY
    #        * (implied) MAX_ARITY
    #        * (implied) NUMBER_OF_RULES
    #  Currently, these fields are stubbed in csg_data.py

    # All decision variables are indexed by node
    rule = intvar(0, NUMBER_OF_RULES - 1, shape = max_n, name="Rules")
    parent = intvar(0, max_n - 1, shape = max_n - 1, name="Parent")
    distance = intvar(0, min(max_n - 1, max_depth), shape = max_n, name="Distance")
    arity = intvar(0, MAX_ARITY, shape = max_n, name="Arity")
    child_index = intvar(0, MAX_ARITY-1, shape = max_n - 1, name="ChildIndex")

    model = Model([
        # Assumption: Node N-1 is the root node. Root node has distance 0 to itself
        distance[max_n - 1] == 0,

        # Enforcing the last min_n nodes are non-empty
        [rule[n] != NUMBER_OF_RULES-1 for n in range(max_n-min_n, max_n)],

        # Non-Root nodes are 1 more away than their parents
        [distance[n] == distance[parent[n]] + 1 for n in range(max_n - 1)],

        # Enforcing the arity according to the tree structure
        [arity[n] == Count(parent, n) for n in range(max_n)],

        # Enforcing the arity according to the number of children per rule
        # Note that '>=' is used instead of the expected '=='
        # This is such that empty rule nodes can freely be added as children
        # This makes it such that we can also find tree with less than max_n nodes
        # We might want to find another way of reducing the number of nodes in the future
        [arity[n] >= Element(RULE_ARITY, rule[n]) for n in range(max_n)],

        # Indexing children of the same parent
        [child_index[0] == 0] + [child_index[n] == Count(parent[:n], parent[n]) for n in range(1, max_n-1)],

        # Enforce the children of each node are of the correct type: TYPES[rule[n]] == CHILD_TYPES[rule[parent[n]], child_index[n]]
        [Element(TYPES, rule[n]) == Element(CHILD_TYPES, MAX_ARITY*Element(rule, parent[n])+child_index[n]) for n in range(max_n-1)]
    ])

    # Solving
    is_optimal = model.solve()
    if is_optimal:
        plot_tree(parent, rule, show_types=True)
    print(model.status())
    return is_optimal

solve(10, 15, max_depth=4)