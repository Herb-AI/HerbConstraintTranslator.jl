from src.pyprogtree.constraints.custom_constraint import CustomConstraint
class SetAncestorRule(CustomConstraint):
    """
    Enforces `ancestor_rule[n]` to align with all parents of node n.
    """
    def decompose(self):
        return [
            [
                (d < self.dv.depth[n] - 1).implies(
                    self.dv.ancestor_rule[n, d] == self.dv.ancestor_rule[self.dv.parent[n], d]
                ) for n in range(self.max_n - 1) for d in range(self.max_depth)
            ],

            [self.dv.ancestor_rule[n, self.dv.depth[n] - 1] == self.dv.rule[self.dv.parent[n]]
             for n in range(self.max_n - 1)],

            [(d >= self.dv.depth[n]).implies(self.dv.ancestor_rule[n, d] == -1)
            for n in range(self.max_n - 1) for d in range(self.max_depth)],
        ]