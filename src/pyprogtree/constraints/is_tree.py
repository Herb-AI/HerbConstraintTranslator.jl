from cpmpy import IfThenElse, Count, Element

from src.pyprogtree.constraints.custom_constraint import CustomConstraint

class IsTree(CustomConstraint):
    """
    Enforces valid values for `depth`, `parent`, `rule` and `arity` according to the Context Free Grammar.
    depth[n]    describes the distance of node n to the root
    parent[n]   holds the index of the parent of node n
    rule[n]     holds the rule index stored in node n
    arity[n]    holds the arity of node n and is consistent with the arity of rule[n]
    """
    def decompose(self):
        return [
            # Assumption: Node N-1 is the root node. Root node has distance 0 to itself.
            self.dv.depth[self.max_n - 1] == 0,

            # Non-root nodes are 1 more deep than their parents
            [self.dv.depth[n] == self.dv.depth[self.dv.parent[n]] + 1 for n in range(self.max_n - 1)],

            # Enforce the children of each node are of the correct type: TYPES[rule[n]] == CHILD_TYPES[rule[parent[n]], child_index[n]]
            [
                (n >= self.dv.init_index).implies(
                    Element(self.g.TYPES, self.dv.rule[n])
                    == Element(self.g.CHILD_TYPES,
                               self.g.MAX_ARITY * Element(self.dv.rule, self.dv.parent[n]) + self.dv.child_index[n]))
                for n in range(self.max_n - 1)
            ],

            # Enforcing the arity according to the tree structure
            [
                IfThenElse(self.dv.init_index == n,
                    self.dv.arity[n] == Count(self.dv.parent, n) - self.dv.init_index,
                    self.dv.arity[n] == Count(self.dv.parent, n)
                ) for n in range(self.max_n)
            ],

            # Enforcing the arity according to the number of children per rule
            [self.dv.arity[n] == Element(self.g.RULE_ARITY, self.dv.rule[n]) for n in range(self.max_n)],
        ]