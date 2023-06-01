from cpmpy import IfThenElse

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