from __future__ import annotations
from enum import Enum
from cpmpy import IfThenElse, intvar, boolvar
from pyprogtree.decision_variables import DecisionVariables
from cpmpy.expressions.python_builtins import any, all

class MatchNode:
    class Location(Enum):
        """
        Method used to tie a MatchNode to an index.
        """
        FIXED_INDEX = 1,    # Location is defined by a 'fixed_index' parameter
        PATH = 2,           # Location is defined by a 'path' parameter, following a specfic ancestor_path
        CHILD = 3,          # Location is defined by a parent MatchNode
        FREE = 4            # Location is not defined, this node can match anywhere

    def __init__(self, rule: int | str, children=None, path=None, fixed_index=None):
        """
        :param rule:            int: 'matchnode': rule index this node should match.
                                str: 'matchvar' rule index should be equal to match nodes with the same string.
        :param children:        list of MatchNodes representing direct children of this MatchNode in order.
        :param path:            ancestor_path to reach this matchnode
        :param fixed_index:     fixed node index this match node should have
        """
        self.rule = rule
        self.children = [] if children is None else children
        self.path = path
        self.fixed_index = fixed_index

    def setup(self, dv: DecisionVariables):
        """
        :param dv:              an object storing all global DecisionVariables
        """
        for child in self.children:
            child.setup(dv)
            
        self.dv = dv
        self.location = MatchNode.Location.FREE

        if self.fixed_index is None:
            self.index = intvar(0, dv.max_n - 1)
            self.exists = boolvar()
        else:
            self.set_location(MatchNode.Location.FIXED_INDEX)
            self.index = self.fixed_index
            self.exists = True

        if self.path is not None:
            self.set_location(MatchNode.Location.PATH)
            self.path += [-1]*(dv.max_depth-len(self.path))
        self.parent = None
        self.child_index = None

        for i, child in enumerate(self.children):
            child.set_location(MatchNode.Location.CHILD)
            child.parent = self.index
            child.child_index = i

        self.matchvars = dict()
        for child in self.children:
            self.matchvars.update(child.matchvars)
        for child in self.children:
            child.matchvars = self.matchvars
        if type(self.rule) == str:
            if not self.rule in self.matchvars:
                self.matchvars[self.rule] = self

        self.enforced = False

    def set_location(self, location: MatchNode.Location):
        assert self.location == MatchNode.Location.FREE, \
            f"MatchNode location ambiguously defined by {location} and {self.location.name}"
        self.location = location

    def enforce_dont_exist(self):
        return (self.index == 0) & (self.exists == False) & all(c.enforce_dont_exist() for c in self.children)

    def _location_exists(self):
        if self.location == MatchNode.Location.CHILD:
            return any((self.dv.child_index[n] == self.child_index) & (self.dv.parent[n] == self.parent) & (n > self.dv.init_index) for n in range(self.dv.max_n-1))
        elif self.location == MatchNode.Location.PATH:
            return any(all(self.dv.ancestor_path[n, d] == self.path[d] for d in range(self.dv.max_depth)) for n in range(self.dv.max_n))
        raise Exception(f"Unable to match location type {MatchNode.Location.name}")

    def _enforce_location(self):
        if self.location == MatchNode.Location.CHILD:
            return self.exists & (self.dv.child_index[self.index] == self.child_index) & (self.dv.parent[self.index] == self.parent)
        elif self.location == MatchNode.Location.PATH:
            return self.exists & all(self.dv.ancestor_path[self.index, d] == self.path[d] for d in range(self.dv.max_depth))
        raise Exception(f"Unable to match location type {MatchNode.Location.name}")

    def _enforce_children(self):
        return all(c.enforce() for c in self.children)

    def enforce(self):
        """
        :return: Constraints that enforces the node to take a valid location, given such a location exists
        """
        assert not self.enforced, "Attempt to enforce a MatchNode twice"

        self.enforced = True
        if self.location == MatchNode.Location.FIXED_INDEX:
            return self._enforce_children()
        return IfThenElse(
            self._location_exists(),
            self._enforce_location() & self._enforce_children(),
            self.enforce_dont_exist()
        )

    def matched(self):
        """
        :return: BoolVar indicating if the MatchNode and all its children are correctly matched in the current tree.
        """
        assert self.enforced, "Unable to check existance of unenforced MatchNode, please call '.enforce()' first"

        # Recursively call all children
        constraints = all(c.matched() for c in self.children)

        # The node must exist
        if self.location != MatchNode.Location.FIXED_INDEX:
            constraints &= self.exists

        if type(self.rule) == str:
            # MatchVars must match each other
            if self.matchvars[self.rule] != self:
                constraints &= (self.dv.spaceship(self.matchvars[self.rule].index, self.index) == 0)
        else:
            # MatchNodes must match their rule
            constraints &= (self.dv.rule[self.index] == self.rule)

        return constraints

    def value(self):
        """
        :return: Node index of the MatchNode
        """
        if self.location == MatchNode.Location.FIXED_INDEX:
            return self.index
        return self.index.value()

    def copy(self, path=None, fixed_index=None):
        children = [child.copy() for child in self.children]
        if path is None and self.location == MatchNode.Location.PATH:
            path = self.path
        if fixed_index is None and self.location == MatchNode.Location.FIXED_INDEX:
            fixed_index = self.index
        node = MatchNode(self.rule, children=children, path=path, fixed_index=fixed_index)
        node.setup(self.dv)
        return node