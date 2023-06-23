from cpmpy import IfThenElse, Count, Element
from pyprogtree.decision_variables import DecisionVariables

def enforce_tree(dv: DecisionVariables):
    """
    Enforces valid values for `depth`, `parent`, `rule` and `arity` according to the Context Free Grammar.
    depth[n]    describes the distance of node n to the root
    parent[n]   holds the index of the parent of node n
    rule[n]     holds the rule index stored in node n
    arity[n]    holds the arity of node n and is consistent with the arity of rule[n]
    """
    return [
        # Assumption: Node N-1 is the root node. Root node has distance 0 to itself.
        dv.depth[dv.max_n - 1] == 0,

        Element(dv.g.TYPES, dv.rule[dv.max_n - 1]) == dv.return_type if dv.return_type != None else [],

        # Non-root nodes are 1 more deep than their parents
        [dv.depth[n] == dv.depth[dv.parent[n]] + 1 for n in range(dv.max_n - 1)],

        [(n >= dv.init_index).implies(dv.depth[n] < dv.max_depth) for n in range(dv.max_n - 1)],

        # Enforce the children of each node are of the correct type: TYPES[rule[n]] == CHILD_TYPES[rule[parent[n]], child_index[n]]
        [
            (n >= dv.init_index).implies(
                Element(dv.g.TYPES, dv.rule[n])
                == Element(dv.g.CHILD_TYPES,
                           dv.g.MAX_ARITY * Element(dv.rule, dv.parent[n]) + dv.child_index[n]))
            for n in range(dv.max_n - 1)
        ],

        # Enforcing the arity according to the tree structure
        [
            IfThenElse(dv.init_index == n,
                dv.arity[n] == Count(dv.parent, n) - dv.init_index,
                dv.arity[n] == Count(dv.parent, n)
            ) for n in range(dv.max_n)
        ],

        # Enforcing the arity according to the number of children per rule
        [dv.arity[n] == Element(dv.g.RULE_ARITY, dv.rule[n]) for n in range(dv.max_n)],
    ]