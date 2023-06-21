# from pyprogtree.decision_variables import DecisionVariables
#
# def enforce_children(dv: DecisionVariables):
#     """
#     Enforces child(n,i) to contain the ith child of node n
#     """
#     print("WARNING: deprecated")
#     return [
#         [dv.child(dv.parent[n], dv.child_index[n]) == n  for n in range(dv.max_n-1)],
#         [(i >= dv.arity[n]).implies(dv.child(n, i) == 0) for n in range(dv.max_n-1) for i in range(dv.g.MAX_ARITY)]
#     ]