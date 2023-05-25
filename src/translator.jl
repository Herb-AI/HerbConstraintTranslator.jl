using PyCall

# Import the python utilities:
py"""
from pyprogtree import runner
"""

# Define a list of production rules alongside IO types (temporary):
prod_rules = [
    ["3", "Real", []],
    ["4", "Real", []],
    ["?", "Real", ["Bool", "Real", "Real"]],
    ["Sqrt", "Real", ["Real"]],
    ["Not", "Bool", ["Bool"]],
    ["&&", "Bool", ["Bool", "Bool"]],
    ["+", "Real", ["Real", "Real"]],
    [">=", "Bool", ["Real", "Real"]],
    ["T", "Bool", []],
    ["F", "Bool", []]
    ]
    
py"runner.run"(prod_rules)
