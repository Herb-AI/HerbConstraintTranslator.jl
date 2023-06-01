from src.pyprogtree.constraints.custom_constraint import CustomConstraint
class SetEmptyNodes(CustomConstraint):
    """
    Enforces nodes before the `init_index` to be empty.
    """
    def decompose(self):
        return [
            # Node is empty iff its before the initial index
            [(n < self.dv.init_index) == (self.dv.rule[n] == self.g.EMPTY_RULE) for n in range(self.max_n)],

            # Empties are leftmost tail
            [(n < self.dv.init_index).implies(self.dv.parent[n] == self.dv.init_index) for n in range(self.max_n - 1)]
        ]