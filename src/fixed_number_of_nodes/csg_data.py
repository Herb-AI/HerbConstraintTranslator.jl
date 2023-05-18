# Empty data lists
TYPES = []
CHILD_TYPES = []
TYPE_NAMES = []
RULE_NAMES = []

# Quick way to add new rules
def add_rule(name, returntype, childtypes):
    global TYPES, CHILD_TYPES, TYPE_NAMES, RULE_NAMES
    RULE_NAMES.append(name)
    for t in [returntype]+childtypes:
        if t not in TYPE_NAMES:
            TYPE_NAMES.append(t)
    TYPES.append(TYPE_NAMES.index(returntype))
    CHILD_TYPES.append([TYPE_NAMES.index(childtype) for childtype in childtypes])

# Define your grammar here
add_rule("3", "Real", [])
add_rule("4", "Real", [])
add_rule("?", "Real", ["Bool", "Real", "Real"])
add_rule("Sqrt", "Real", ["Real"])
add_rule("Not", "Bool", ["Bool"])
add_rule("&&", "Bool", ["Bool", "Bool"])
add_rule("+", "Real", ["Real", "Real"])
add_rule(">=", "Bool", ["Real", "Real"])
add_rule("T", "Bool", [])
add_rule("F", "Bool", [])

# Adding the empty rule as the final rule, TYPE[-1] is reserved for as the empty rule type ""
add_rule("", "", [])

# Implicit global variables
RULE_ARITY = [len(l) for l in CHILD_TYPES]
MAX_ARITY = max(RULE_ARITY)
NUMBER_OF_RULES = len(RULE_NAMES)

#flatten CHILD_TYPES into a 1D list
for i in range(len(CHILD_TYPES)):
    while len(CHILD_TYPES[i]) < MAX_ARITY:
        CHILD_TYPES[i] += [TYPES[-1]]
CHILD_TYPES = sum(CHILD_TYPES, [])
assert len(CHILD_TYPES) == NUMBER_OF_RULES*MAX_ARITY, "Unexpected length of flattened CHILD_TYPES"