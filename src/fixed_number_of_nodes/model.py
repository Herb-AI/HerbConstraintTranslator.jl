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

    max_depth = min(max_n - 1, max_depth)

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
    parent = intvar(-1, max_n-1, shape = max_n, name="Parent")
    depth = intvar(0, max_depth, shape = max_n, name="Distance")
    arity = intvar(0, MAX_ARITY, shape = max_n, name="Arity")
    child_index = intvar(0, MAX_ARITY-1, shape = max_n, name="ChildIndex")
    subtree_size = intvar(0, max_n, shape = max_n, name="SubtreeSize")

    def grand_parent(k, n):
        """
        Example: grand_parent(3, n) == parent[parent[parent[n]]]
        :return: k'th order grandparent of n
        """
        if k == 0:
            return n
        return parent[grand_parent(k-1, n)]

    def uncle_ordering(k, n):
        """
        Example: 0'th order uncle is your left brother
        Example: 1'th order uncle is your left uncle
        Example: 2'th order uncle is the left uncle of your parent
        :return: constraint that enforces index[n] > index[k'th order uncle]
        """
        return [((arity[n] == 0) & (child_index[grand_parent(k, n)] > 0) & (child_index[uncle] == 0) & (parent[uncle] == parent[grand_parent(k, n)]))
                .implies(n > uncle) for uncle in range(0, max_n - 1)]

    model = Model([
        # Assumption: Node N-1 is the root node. Root node has distance 0 to itself.
        depth[max_n - 1] == 0,

        # Assumption: the root is its own parent.
        parent[max_n - 1] == max_n - 1,

        # Enforcing the last min_n nodes are non-empty
        [rule[n] != EMPTY_RULE for n in range(max_n-min_n, max_n)],

        # Non-Root nodes are 1 more away than their parents
        [depth[n] == depth[parent[n]] + 1 for n in range(max_n - 1)],

        # Enforcing the arity according to the tree structure
        [arity[n] == Count(parent, n) for n in range(max_n)],

        # Enforcing the arity according to the number of children per rule
        # Note that '>=' is used instead of the expected '=='
        # This is such that empty rule nodes can freely be added as children
        # This makes it such that we can also find tree with less than max_n nodes
        # We might want to find another way of reducing the number of nodes in the future
        [arity[n] == Element(RULE_ARITY, rule[n]) for n in range(max_n)],

        # Indexing children of the same parent
        [child_index[0] == 0] + [child_index[n] == Count(parent[:n], parent[n]) for n in range(1, max_n-1)],

        # Enforce the children of each node are of the correct type: TYPES[rule[n]] == CHILD_TYPES[rule[parent[n]], child_index[n]]
        [Element(TYPES, rule[n]) == Element(CHILD_TYPES, MAX_ARITY*Element(rule, parent[n])+child_index[n]) for n in range(max_n-1)],

        ########################################################################
        ##########     WIP: Constraints for Traversal Order below     ##########
        ########################################################################

        # Calculate the subtree size for each node
        # todo: subtree_size is yet unused, but maybe helpful for the traversal order
        [subtree_size[n] == 1 + sum([(parent[child] == n) * subtree_size[child] for child in range(max_n - 1)]) for n in
         range(max_n)],

        # (a) Node 0 is the first node of left-first depth-first traversal
        [child_index[grand_parent(k, 0)] == 0 for k in range(max_depth)],

        # (b) Parents go immediately after their right child
        [(child_index[n] == arity[parent[n]] - 1).implies(parent[n] == n + 1) for n in range(0, max_n - 1)],

        # (c) Leaf nodes go immediately after their left brother
        [[((arity[n] == 0) & (parent[brother] == parent[n]) & (child_index[brother] == child_index[n] - 1)).implies(n == brother + 1)
           for brother in range(0, max_n - 1)] for n in range(0, max_n - 1)],

        # (c') Lead nodes have to respect uncle ordering
        # todo: optimize these very, very expensive ordering constraints
        [[uncle_ordering(k, n) for n in range(max_n - 1)] for k in range(max_depth)]
    ])

    # Solving
    is_optimal = model.solve()
    if is_optimal:
        plot_tree(parent, rule,
                  show_types=False,
                  show_rules=True,
                  show_node_index=True,
                  show_empty_nodes=True,
                  show_lambda_string=lambda n: f"{''}")
    print(model.status())
    return is_optimal

solve(15, 15, max_depth=4)