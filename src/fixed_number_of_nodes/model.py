from cpmpy import intvar, Model
from cpmpy.expressions.globalconstraints import Element
from plot_tree import plot_tree
from csg_data import *

# Fixed Number of nodes
N = 15

# All DVs are arrays for each node
rule = intvar(0, NUMBER_OF_RULES - 1, shape = N, name="Rules")
parent = intvar(0, N - 1, shape = N - 1, name="Parent")
distance = intvar(0, N - 1, shape = N, name="Distance")
arity = intvar(0, max(RULE_ARITY), shape = N, name="Arity")
m = Model()

# Assumption: Node N-1 is the root node. Root node has distance 0 to itself
m += [distance[N - 1] == 0]

# Non-Root nodes are 1 more away than their parents
m += [distance[n] == distance[parent[n]] + 1 for n in range(N - 1)]

# Enforcing the arity according to the tree structure
m += [arity[n] == sum([parent[c] == n for c in range(N-1)]) for n in range(N)]

# Enforcing the arity according to the number of children per rule
m += [arity[n] == Element(RULE_ARITY, rule[n]) for n in range(N)]

# Enforce that the children of a node are of the expected type
# todo: for c in children(n): type(c) == CHILD_TYPES[n, c]

# Solving
if m.solve():
    plot_tree(parent, rule)
print(m.status())