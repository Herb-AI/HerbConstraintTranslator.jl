from __future__ import annotations
from enum import Enum
from cpmpy import IfThenElse, intvar
from src.pyprogtree.decision_variables import DecisionVariables
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

    def __init__(self, dv: DecisionVariables, rule: int | str, children=None, path=None, fixed_index=None):
        """
        :param dv:              an object storing all global DecisionVariables
        :param rule:            int: 'matchnode': rule index this node should match.
                                str: 'matchvar' rule index should be equal to match nodes with the same string.
        :param children:        list of MatchNodes representing direct children of this MatchNode in order.
        :param path:            ancestor_path to reach this matchnode
        :param fixed_index:     fixed node index this match node should have
        """
        self.dv = dv
        self.rule = rule
        self.location = MatchNode.Location.FREE

        if fixed_index is None:
            self.index = intvar(-1, dv.max_n - 1)
        else:
            self.set_location(MatchNode.Location.FIXED_INDEX)
            self.index = fixed_index

        if path is None:
            self.path = None
        else:
            self.set_location(MatchNode.Location.PATH)
            self.path = path
            self.path += [dv.g.MAX_ARITY]*(dv.max_depth-len(self.path))
        self.parent = None
        self.child_index = None

        self.children = [] if children is None else children
        for i, child in enumerate(self.children):
            child.set_location(MatchNode.Location.CHILD)
            child.parent = self.index
            child.child_index = i

        self.enforced = False

    def set_location(self, location: MatchNode.Location):
        assert self.location == MatchNode.Location.FREE, \
            f"MatchNode location ambiguously defined by {location} and {self.location.name}"
        self.location = location

    def _has_fixed_index(self):
        return type(self.index) == int

    def _location_exists(self):
        if self.location == MatchNode.Location.CHILD:
            return any((self.dv.child_index[n] == self.child_index) & (self.dv.parent[n] == self.parent) for n in range(self.dv.max_n-1))
        elif self.location == MatchNode.Location.PATH:
            return any(all(self.dv.ancestor_path[n, d] == self.path[d] for d in range(self.dv.max_depth)) for n in range(self.dv.max_n))
        raise Exception(f"Unable to match location type {MatchNode.Location.name}")

    def _enforce_location(self):
        if self.location == MatchNode.Location.CHILD:
            return (self.dv.child_index[self.index] == self.child_index) & (self.dv.parent[self.index] == self.parent)
        elif self.location == MatchNode.Location.PATH:
            return all(self.dv.ancestor_path[self.index, d] == self.path[d] for d in range(self.dv.max_depth))
        raise Exception(f"Unable to match location type {MatchNode.Location.name}")

    def _enforce_children(self):
        return all(c.enforce() for c in self.children)

    def enforce(self):
        """
        :return: Constraints that enforces the node to take a valid location, given such a location exists
        """
        assert type(self.rule) != str, f"Unresolved MatchVar '{self.rule}'"
        assert not self.enforced, "Attempt to enforce a MatchNode twice"

        self.enforced = True
        if self.location == MatchNode.Location.FREE:
            return (self._enforce_children()) & (self.index >= self.dv.init_index)
        elif self.location == MatchNode.Location.FIXED_INDEX:
            return self._enforce_children()
        return IfThenElse(
            self._location_exists(),
            self._enforce_children() & self._enforce_location(),
            self.index == -1
        )

    def matched(self):
        """
        :return: BoolVar indicating if the MatchNode and all its children are correctly matched in the current tree.
        """
        assert self.enforced, "Unable to check existance of unenforced MatchNode, please call '.enforce()' first"
        exists = (self.dv.rule[self.index] == self.rule) & all(c.matched() for c in self.children)
        if self.location != MatchNode.Location.FREE:
            exists &= (self.index != -1)
        return exists

    def value(self):
        """
        :return: Node index of the MatchNode
        """
        if self.location == MatchNode.Location.FIXED_INDEX:
            return self.index
        return self.index.value()
