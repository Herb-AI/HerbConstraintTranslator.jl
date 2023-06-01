from src.pyprogtree.constraints.custom_constraint import CustomConstraint
class SetAncestorPath(CustomConstraint):
    """
    Enforces `ancestor_path[n, d]` to store the `child_index[m]` of all parents m of node n
    """
    def decompose(self):
        return [
            # Fix ancestor path of the root
            [self.dv.ancestor_path[self.max_n - 1, d] == self.g.MAX_ARITY for d in range(self.max_depth)],

            # Enforce each node's path to be an extension of its parents path
            [
                (d < self.dv.depth[n] - 1).implies(
                    self.dv.ancestor_path[n, d]
                    == self.dv.ancestor_path[self.dv.parent[n], d])
                for n in range(self.max_n - 1) for d in range(self.max_depth)
            ],

            # Enforce each non-root node's last path symbol to be its child index
            [self.dv.ancestor_path[n, self.dv.depth[n] - 1] == self.dv.child_index[n] for n in range(self.max_n - 1)],

            # Enforce the remaining path symbols to be max_arity
            [
                (d >= self.dv.depth[n]).implies(
                    self.dv.ancestor_path[n, d] == self.g.MAX_ARITY
                )
                for n in range(self.max_n - 1) for d in range(self.max_depth)
            ],
        ]