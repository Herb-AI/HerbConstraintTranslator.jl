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
add_rule("0", "Real", [])
add_rule("1", "Real", [])
add_rule("2", "Real", [])
add_rule("3", "Real", [])
add_rule("Sqrt", "Real", ["Real"])
add_rule("+", "Real", ["Real", "Real"])
add_rule("*", "Real", ["Real", "Real"])
add_rule("==", "Bool", ["Real", "Real"])
add_rule("T", "Real", [])
add_rule("F", "Real", [])

# IMPORTANT: Adding empty rules for CPMPY encoding
# add_rule(" ", "EmptyRuleType", ["EmptyRuleType"]) #allows dead trails of emptyrules
add_rule(" ", "EmptyRuleType", [])
RULE_ARITY = [len(l) for l in CHILD_TYPES]
NUMBER_OF_RULES = len(RULE_NAMES)