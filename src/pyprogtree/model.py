from math import log, ceil
from cpmpy import intvar, Model
from cpmpy.expressions.globalconstraints import Element, Count
from src.pyprogtree.grammar import *
from src.pyprogtree.plot_tree import plot_tree
import numpy as np

def solve(g, min_n, max_n, max_depth=float("inf")):
    """
    Finds a feasible AST using global variables from 'csg_data.py', then plots it.
    :param g: grammar encoding
    :param min_n: minimum number of nodes in the tree
    :param max_n: maximum number of nodes in the tree
    :param max_depth: (optional) maximum depth of the tree
    :return:
    """

    max_depth = max_n - 1 #min(max_n - 1, max_depth)

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
    rule = intvar(0, g.NUMBER_OF_RULES - 1, shape = max_n, name="Rules")
    parent = intvar(-1, max_n-1, shape = max_n-1, name="Parent")
    depth = intvar(0, max_depth, shape = max_n, name="Distance")
    arity = intvar(0, g.MAX_ARITY, shape = max_n, name="Arity")
    child_index = intvar(0, g.MAX_ARITY-1, shape = max_n, name="ChildIndex")
    ancestor_path = intvar(0, g.MAX_ARITY, shape = (max_n, max_n-1), name="AncestorPath")

    number_of_empty_nodes = intvar(0, min_n, name="NumberOfEmptyNodes")

    base = np.array([(g.MAX_ARITY + 1) ** i for i in range(max_n-1)][::-1])

    model = Model([
        # Assumption: Node N-1 is the root node. Root node has distance 0 to itself.
        depth[max_n - 1] == 0,

        # Non-Root nodes are 1 more away than their parents
        [depth[n] == depth[parent[n]] + 1 for n in range(max_n - 1)],

        # Enforcing the arity according to the tree structure
        [arity[n] == Count(parent, n) for n in range(max_n)],

        # Enforcing the arity according to the number of children per rule
        [(n > number_of_empty_nodes).implies(arity[n] == Element(g.RULE_ARITY, rule[n])) for n in range(1, max_n)],

        # Enforcing the number of empty nodes
        [(n < number_of_empty_nodes).implies(rule[n] == g.EMPTY_RULE) for n in range(max_n)],

        # Enforce the inner nodes of the trail of empty nodes have arity 1
        [(n <= number_of_empty_nodes).implies(arity[n] == 1) for n in range(1, max_n)],

        # Indexing children of the same parent
        [child_index[0] == 0] + [child_index[n] == Count(parent[:n], parent[n]) for n in range(1, max_n-1)],

        # Enforce the children of each node are of the correct type: TYPES[rule[n]] == CHILD_TYPES[rule[parent[n]], child_index[n]]
        [Element(g.TYPES, rule[n]) == Element(g.CHILD_TYPES, g.MAX_ARITY*Element(rule, parent[n])+child_index[n]) for n in range(max_n-1)],

        # Fix ancestor path of the root
        [ancestor_path[max_n-1, d] == g.MAX_ARITY for d in range(max_n-1)],

        # Enforce each node's path to be an extension of its parents path 
        [(d < depth[n]-1).implies(ancestor_path[n, d] == ancestor_path[parent[n], d]) for n in range(max_n-1) for d in range(max_n-1)],

        # Enforce each non-root node's last path symbol to be its child index
        [ancestor_path[n, depth[n]-1] == child_index[n] for n in range(max_n-1)],

        # Enforce the remaining path symbols to be max_arity
        [(d >= depth[n]).implies(ancestor_path[n, d] == g.MAX_ARITY) for n in range(max_n-1) for d in range(max_n-1)],

        # Enfoce a lexicographic ordering (NOTE: might suffer from integer overflow issue as the sums quickly get very large)
        [sum(ancestor_path[n] * base) < sum(ancestor_path[n+1] * base) for n in range(max_n-1)]
    ])

    # Solving
    is_optimal = model.solve()
    if is_optimal:
        plot_tree(g, parent, rule,
                  show_types=False,
                  show_rules=True,
                  show_node_index=True,
                  show_empty_nodes=True,
                  show_lambda_string=lambda n: f"{''}")
    print(model.status())
    return is_optimal
