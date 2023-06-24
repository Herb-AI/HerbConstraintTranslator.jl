import numpy as np
from cpmpy import intvar
from cpmpy.expressions.core import Expression

from pyprogtree.grammar import Grammar

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
        self.rule                   =  intvar( 0, g.NUMBER_OF_RULES - 1, shape=(max_n,),                        name="Rules")
        self.parent                 =  intvar(-1, max_n-1,               shape=(max_n-1,),                      name="Parent")
        self.depth                  =  intvar( 0, max_depth,             shape=(max_n,),                        name="Depth")
        self.arity                  =  intvar( 0, g.MAX_ARITY,           shape=(max_n,),                        name="Arity")
        self.child_index            =  intvar( 0, g.MAX_ARITY-1,         shape=(max_n,),                        name="ChildIndex")
        # self.children_1D            =  intvar( 0, max_n-2,               shape=max_n*g.MAX_ARITY,               name="Children")
        self.init_index             =  intvar( 0, max_n-min_n,           shape=1,                               name="InitialIndex")
        self.ancestor_path          =  intvar(-1, g.MAX_ARITY - 1,       shape=(max_n, max_depth),              name="AncestorPath")
        self.ancestor_rule          =  intvar(-1, g.NUMBER_OF_RULES - 1, shape=(max_n-1, max_depth),            name="AncestorRule")
        self.treesize               =  intvar( 1, max_n,                 shape=(max_n,),                        name="TreeSize")
        self.spaceship_1D           =  intvar(-1, 1,                     shape=(max_n-1)**3,                    name="<=>")
        self.leftright_rule_indexes = [intvar(-1, max_n-1,               shape=1,                               name=f"LeftRightRule{i}Indexes") 
                                       if dim > 0 
                                       else None 
                                       for i, dim in enumerate(g.LEFTRIGHT_DIMENSIONS)]
        
        self.topdown_rule_indexes  = [[intvar(0,  max_depth+1,           shape=(dim,),                          name=f"TopDown{n}Rule{i}Indexes") 
                                       if dim > 0 
                                       else None 
                                       for i, dim in enumerate(g.TOPDOWN_DIMENSIONS)]
                                    for n in range(max_n - 1)]
        print("DONE")

        self.solutions = []

    # def child(self, node_index, child_index):
    #     return self.children_1D[node_index * self.g.MAX_ARITY + child_index]

    def spaceship_helper(self, n, m, k):
        return self.spaceship_1D[n+ m*(self.max_n-1) + k*(self.max_n-1)**2]

    def spaceship(self, n, m):
        """
        Compares the ordering of the subtrees of n and m.
        :param n: node n
        :param m: node m
        :return: -1 if subtree(n) < subtree(m)
                 0 if subtree(n) == subtree(m)
                 1 if subtree(n) <=> subtree(m)
        """
        return self.spaceship_helper(n, m, self.treesize[m]-1)

    def save_solution(self):
        """
        Saves a dictionary of values of all decision variables as a new solution
        """
        new_solution = dict()
        for name, variable in self.__dict__.items():
            if isinstance(variable, Expression):
                new_solution[name] = variable.value()
        self.solutions.append(new_solution)

    def compare_solutions(self):
        duplicate_solutions = set()
        for i in range(len(self.solutions)):
            sol1 = self.solutions[i]
            if i in duplicate_solutions:
                continue
            for j in range(i):
                sol2 = self.solutions[j]
                assert sol1.keys() == sol2.keys(), "Solutions have a different number of keys"
                differences = []
                for name in sol1.keys():
                    if np.any(sol1[name] != sol2[name]):
                        differences.append(name)
                # print("----------------------------------")
                # print(f"differences of solution ({i}, {j}): {differences}:")
                # for name in differences:
                #     print(name, sol1[name])
                #     print(name, sol2[name])
                # print("----------------------------------")
                if len(differences) == 0:
                    duplicate_solutions.add(j)
        return len(duplicate_solutions)
