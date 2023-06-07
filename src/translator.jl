# Import the python utilities:

py"""
from pyprogtree import runner
"""

ListedRule = Vector{Union{String, Vector{String}}}

# Define a list of production rules alongside IO types (temporary):
function solve(grammar::ContextSensitiveGrammar)
    encoding = translate(grammar)
    ruletypes, childtypes, typenames, rulenames = encoding

    # call with our params
    #py"runner.run"(prod_rules)
end

function translateConstraint(c::Constraint)::ListedRule
    return [] #TODO
end

function translate(grammar::ContextSensitiveGrammar)::Tuple{Vector{Int}, Vector{Vector{Int}}, Vector{String}, Vector{String}}
    typenames  = collect(keys(grammar.bytype))
    typeindex  = Dict(zip(typenames, 0:length(typenames)-1))
    # rename type symbols with their indeces
    ruletypes  = map(t -> typeindex[t], grammar.types) # what if a type is `Nothing`?
    childtypes = map(typs -> map(t -> typeindex[t], typs), grammar.childtypes)
    # compute this in the constructor of the Grammar class
    #rulearity  = map(length, grammar.childtypes)
    #maxarity   = max(rulearity)
    #numrules   = length(grammar.rules)
    rulenames = Vector()
    for (i, rule) ∈ enumerate(grammar.rules)
        if rule isa Expr
            if rule.head == :call
                push!(rulenames, string(rule.args[1]))
            else
                push!(rulenames, string(rule.head))
            end
        elseif rule isa Symbol
            push!(rulenames, string(rule))
        else
            push!(rulenames, string(i))
        end
    end
    #constraints = map(translateConstraint, grammar.constraints)
    return (ruletypes, childtypes, map(string, typenames), rulenames)
end