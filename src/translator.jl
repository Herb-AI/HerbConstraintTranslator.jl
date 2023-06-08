# Import the python utilities:

py"""
from pyprogtree import runner
"""

ListedRule = Vector{Union{String, Vector{String}}}

function solve(grammar::ContextSensitiveGrammar)
    ruletypes, childtypes, typenames, rulenames = translate(grammar)

    # call with our params
    py"runner.run"(ruletypes, childtypes, typenames, rulenames)
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