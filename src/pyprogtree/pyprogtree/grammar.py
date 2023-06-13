from pyprogtree.decision_variables import DecisionVariables
from pyprogtree.match_node import MatchNode

class Grammar:
    def __init__(self, ruletypes, childtypes, typenames, rulenames, constraints):
        print("init grammar")
        self.TYPES = ruletypes
        self.CHILD_TYPES = childtypes
        self.TYPE_NAMES = typenames
        self.RULE_NAMES = rulenames

        # Constraints
        self.TOPDOWN_ORDERED = []
        self.LEFTRIGHT_ORDERED = []
        self.TOPDOWN_FORBIDDEN = []
        self.SUBTREE_ORDERED = []
        self.SUBTREE_FORBIDDEN = []

        self.add_rule("", "", [])
        self.update_implicit_vars()
        self.flatten_child_types()
        self.add_constraints(constraints)

    # Quick way to add new rules:
    def add_rule(self, name, returntype, childtypes):
        self.RULE_NAMES.append(name)
        for t in [returntype]+childtypes:
            if t not in self.TYPE_NAMES:
                self.TYPE_NAMES.append(t)
        self.TYPES.append(self.TYPE_NAMES.index(returntype))
        self.CHILD_TYPES.append([self.TYPE_NAMES.index(childtype) for childtype in childtypes])

    def add_rules(self, rules):
        # Add rules from the rules of the original grammar
        for rule in rules:
            self.add_rule(*rule)

        # Adding the empty rule as the final rule, TYPE[-1] is reserved for as the empty rule type ""
        self.add_rule("", "", [])
        
    def update_implicit_vars(self):
        # Implicit global variables
        self.RULE_ARITY = [len(l) for l in self.CHILD_TYPES]
        self.MAX_ARITY = max(self.RULE_ARITY)
        self.NUMBER_OF_RULES = len(self.RULE_NAMES)
        self.EMPTY_RULE = self.NUMBER_OF_RULES - 1

    def flatten_child_types(self):
        #flatten CHILD_TYPES into a 1D list
        for i in range(len(self.CHILD_TYPES)):
            while len(self.CHILD_TYPES[i]) < self.MAX_ARITY:
                self.CHILD_TYPES[i] += [self.TYPES[-1]]
        self.CHILD_TYPES = sum(self.CHILD_TYPES, [])
        assert len(self.CHILD_TYPES) == self.NUMBER_OF_RULES*self.MAX_ARITY, "Unexpected length of flattened CHILD_TYPES"

    def grammar_from_rules(self, rules):
        self.add_rules(rules)
        self.update_implicit_vars()
        self.flatten_child_types()

    def add_constraints(self, constraints):
        for const in constraints:
            if const[0] == "TDO":
                self.TOPDOWN_ORDERED.append(const[1])
            elif const[0] == "LRO":
                self.LEFTRIGHT_ORDERED.append(const[1])
            elif const[0] == "TDF":
                self.TOPDOWN_FORBIDDEN.append(const[1])
            elif const[0] == "O" or const[0] == "LO":
                self.SUBTREE_ORDERED.append(const[1])
            elif const[0] == "F" or const[0] == "LF":
                self.SUBTREE_FORBIDDEN.append(const[1])
            else:
                raise Exception("Could not find the intended constraint!")
