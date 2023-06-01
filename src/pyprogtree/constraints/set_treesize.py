from src.pyprogtree.constraints.custom_constraint import CustomConstraint
class SetTreeSize(CustomConstraint):
    """
    Sets `treesize[n]` to the number of nodes in the subtree rooted at node n
    """
    def decompose(self):
        return [
            # Calculate the treesize for each node
            [self.dv.treesize[n] ==
                1 + sum([((self.dv.parent[child] == n) & (child >= self.dv.init_index)) * self.dv.treesize[child]
            for child in range(self.max_n - 1)]) for n in range(self.max_n)],

            # Implicit constraint that fixes the treesize of the root, to potentially improve performance
            self.dv.treesize[self.max_n - 1] == self.max_n - self.dv.init_index
        ]