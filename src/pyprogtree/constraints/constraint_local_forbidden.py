#todo: local forbidden
from src.pyprogtree.decision_variables import DecisionVariables

def constraint_local_forbidden(dv: DecisionVariables):
    pass

# from __future__ import annotations
# from cpmpy import IfThenElse, Table, intvar
# from src.pyprogtree.decision_variables import DecisionVariables
#
# def constraint_local_forbidden(dv: DecisionVariables, path=[-1, -1, -1, -1]):
#     n1 = intvar(-1, dv.max_n-1)
#
#     return [IfThenElse(
#         [dv.ancestor_path[n1, d] == path[d] for d in dv.max_depth],
#         Table(path, dv.ancestor_path),
#         n1 == -1,
#         n1 == -1
#     )]  # n1 is the root

#     self.match_vars = dict()
#     self._resolve_matchvars()
#
# def _resolve_matchvars(self):
#     for child in self.children:
#         self.match_vars.update(child.match_vars)
#     if type(self.rule) == str:
#         if not self.rule in self.match_vars:
#             self.match_vars[self.rule] = self.dv.rule[self.index]
#         self.rule = self.match_vars[self.rule]

# self.children = children
# self.match_vars = dict()
# for child in self.children:
#     self.match_vars += child.match_vars
# for child in self.children:
#     if type(self.rule) == str:
#         if not self.rule in self.match_vars:
#             self.match_vars[child.rule] = dv.rule[child.index]
#         self.rule = self.match_vars[child.rule]

# class LocalForbidden:
#     def __init__(self, dv: DecisionVariables):
#         self.dv = dv
#
#
# def LocalForbidden():
#     def __init__(child_index=None, ancestors_path=None):
#
#     path = [-1, -1, -1, -1]
#     IfThenElse(
#         Table(path, ancestors_path)
#         [ancestors_path[n1, d] == path[d] for d in max_depth],
#     n1 == -1
#     )  # n1 is the root
#
#     IfThenElse(
#         n1 != -1
#         (parent(n2) == n1, child_index[n2] == 0)
#     n2 == -1
#     )  # n2 is the correct child of n1
#
#     IfThenElse(
#         n1 != -1
#         (parent(n3) == n1, child_index[n3] == 1)
#     n3 == -1
#     )  # n3 is the correct child of n1
#
#     (n1 != -1, n2 != -1, n3 != -1) = > rule[n1] == 10 and spaceshape([n3, n2]) == 0