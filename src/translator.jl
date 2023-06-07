# Import the python utilities:

py"""
from pyprogtree import runner
"""

ListedRule = Vector{Union{String, Vector{String}}}

# Define a list of production rules alongside IO types (temporary):
function run()
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
    #=
    encoding = translate(grammar)
    ruletypes, childtypes, typenames = encoding
    println(ruletypes)
    println(childtypes)
    println(typenames)
    =#
    #println(rulenames)
    py"runner.run"(prod_rules)
end

#=
function translateConstraint(c::Constraint)::ListedRule
    return [] #TODO
end
=#
function translate(grammar::ContextSensitiveGrammar)::Any
    typenames  = keys(grammar.bytype)
    typeindex  = Dict(zip(typenames, 0:length(typenames)-1))
    ruletypes  = map(t -> typeindex[t], grammar.types) # what if a type is `Nothing`?
    childtypes = map(typs -> map(t -> typeindex[t], typs), grammar.childtypes)
    # compute this in the constructor of the Grammar class
    #rulearity  = map(length, grammar.childtypes)
    #maxarity   = maximum(rulearity)
    #numrules   = length(grammar.rules)
    #=
    rulenames  = map(
        ((i, _)) -> String(i),
        #rule -> if (rule.head == :call) rule.args[1] else rule.head end, 
        enumerate(grammar.rules)
    )=#
    #constraints = map(translateConstraint, grammar.constraints)

    return (ruletypes, childtypes, typenames)
end

#=translate(Herb.HerbGrammar.@csgrammar begin
    Real = x
    Real = |(0:3)
    Real = Real + Real
end)=#