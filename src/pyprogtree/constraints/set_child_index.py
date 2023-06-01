from cpmpy import IfThenElse, Count, Element

from src.pyprogtree.constraints.custom_constraint import CustomConstraint

class SetChildIndex(CustomConstraint):
    """
    Enforces `child_index` to index non-empty children of the same parent.

    Example:
        nodes 5, 6 and 9 are children of parent 17 -->
        child_index[5] = 0
        child_index[6] = 1
        child_index[9] = 2
    """
    def decompose(self):
        return [
            # Indexing children of the same parent
            [(n > self.dv.init_index).implies(self.dv.child_index[n] == Count(self.dv.parent[:n], self.dv.parent[n]))
            for n in range(1, self.max_n - 1)],

            # Child index of empty nodes and the initial node is 0
            [(n <= self.dv.init_index).implies(self.dv.child_index[n] == 0) for n in range(0, self.max_n - 1)]
        ]