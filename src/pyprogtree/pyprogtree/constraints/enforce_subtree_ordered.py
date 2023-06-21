from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.match_node import MatchNode
from cpmpy.expressions.python_builtins import all

def enforce_subtree_ordered(dv: DecisionVariables):
    constraints = []
    for pair in dv.g.SUBTREE_ORDERED:
        #expects pair[0] to hold a MatchNode
        #expects pair[1] to hold an order
        pair[0].setup(dv)
        if pair[0].location == MatchNode.Location.FREE:
            constraints.append(constraint_ordered(dv, pair[0], pair[1]))
        else:
            constraints.append(constraint_local_ordered(dv, pair[0], pair[1]))
    return constraints

def constraint_local_ordered(dv: DecisionVariables, match_node: MatchNode, order: list):
    """
    MatchVars in the 'match_node' should be ascending in the given 'order'
    """
    assert match_node.location != MatchNode.Location.FREE, \
        "The 'location' of a MatchNode of a LOCAL ordered constraint should be LOCAL. " + \
        "Please add 'path' or 'fixed_index' parameters to the 'match_node'"

    index = []
    for symbol in order:
        assert symbol in match_node.matchvars, "'{symbol}' not in MatchNode"
        index.append(match_node.matchvars[symbol].index)

    return (match_node.enforce()) & (match_node.matched().implies(
        all(match_node.dv.spaceship(index[i], index[i+1]) >= 0 for i in range(len(index)-1))
    ))

def constraint_ordered(dv: DecisionVariables, match_node: MatchNode, order: list):
    assert match_node.location == MatchNode.Location.FREE, \
        "The 'location' of a MatchNode of GLOBAL ordered constraint should be GLOBAL. " + \
        "Please remove 'path' or 'fixed_index' parameters from the 'match_node'"
    match_nodes = [match_node.copy(fixed_index=n) for n in range(dv.max_n)]
    return [constraint_local_ordered(dv, match_nodes[n], order) for n in range(dv.max_n)]