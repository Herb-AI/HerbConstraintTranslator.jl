class Grammar:
    def __init__(self, rules, constraints):
        self.TYPES = []
        self.CHILD_TYPES = []
        self.TYPE_NAMES = []
        self.RULE_NAMES = []
        self.RULE_ARITY = []
        self.MAX_ARITY = 0
        self.NUMBER_OF_RULES = 0
        self.EMPTY_RULE = -1

        # Constraints
        self.TOPDOWN_ORDERED = []
        self.LEFTRIGHT_ORDERED = []
        self.TOPDOWN_FORBIDDEN = []

        # Set variables:
        self.grammar_from_rules(rules)
        self.add_constraints(constraints)

        print("TDF", self.TOPDOWN_FORBIDDEN)

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
            match const[0]:
                case "TDO": self.TOPDOWN_ORDERED.append(const[1])
                case "LRO": self.LEFTRIGHT_ORDERED.append(const[1])
                case "TDF": self.TOPDOWN_FORBIDDEN.append(const[1])
                case _: raise Exception("Could not find the intended constraint!")