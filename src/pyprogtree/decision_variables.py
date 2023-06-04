from cpmpy import intvar
from src.pyprogtree.grammar import Grammar

class DecisionVariables:
    def __init__(self, g: Grammar, min_n: int, max_n: int, max_depth: int):
        """
        :param g:           Context Free Grammar to encode.
        :param min_n:       Minimum number of nodes in the tree.
        :param max_n:       Maximum number of nodes in the tree.
        :param max_depth:   Maximum depth of the tree.
        """
        self.g = g
        self.min_n = min_n
        self.max_n = max_n
        self.max_depth = max_depth

        print("Setting up decision variables... ", end='')
        self.rule                = intvar(0,  g.NUMBER_OF_RULES - 1, shape=max_n,                        name="Rules")
        self.parent              = intvar(-1, max_n-1,               shape=max_n-1,                      name="Parent")
        self.depth               = intvar(0,  max_depth,             shape=max_n,                        name="Distance")
        self.arity               = intvar(0,  g.MAX_ARITY,           shape=max_n,                        name="Arity")
        self.child_index         = intvar(0,  g.MAX_ARITY-1,         shape=max_n,                        name="ChildIndex")
        self.init_index          = intvar(0,  max_n-min_n,           shape=1,                            name="InitialIndex")
        self.ancestor_path       = intvar(0,  g.MAX_ARITY,           shape=(max_n, max_depth),           name="AncestorPath")
        self.ancestor_rule       = intvar(-1, g.NUMBER_OF_RULES - 1, shape=(max_n-1, max_depth),         name="AncestorRule")
        self.treesize            = intvar(1,  max_n,                 shape=max_n,                        name="TreeSize")
        self.spaceship_helper    = intvar(-1, 1,                     shape=(max_n-1, max_n-1, max_n-1),  name="<=>")
        self.topdown_ordered     = intvar(0,  max_depth+1,           shape=(max_n-1, g.TDO_IDXS[-1]),    name="TopDownOrdered")

        print("DONE")

    def spaceship(self, n, m):
        """
        Compares the ordering of the subtrees of n and m
        :param n: node n
        :param m: node m
        :return: -1 if subtree(n) < subtree(m)
                 0 if subtree(n) == subtree(m)
                 1 if subtree(n) <=> subtree(m)
        """
        if n == m:
            return 0
        n, m = max(n, m), min(n, m)
        return self.spaceship_helper[n, m, self.treesize[m]-1]