# Import the python utilities:

py"""
from pyprogtree import runner
"""

ListedRule = Vector{Union{String, Vector{String}}}

function solve(grammar::ContextSensitiveGrammar)
    # Encode the grammar:
    ruletypes, childtypes, typenames, rulenames = translate(grammar)

    # Solve and obtain decision variables (parent, rule):
    parent, rule = py"runner.run"(ruletypes, childtypes, typenames, rulenames)
    parent = map(p -> convert(Int64, p) + 1, parent) # Convert from Int32 to Int64 (for consistency) and shift by 1 to the right (Julia indices)
    rule = map(r -> convert(Int64, r) + 1, rule) # Convert from Int32 to Int64 (for consistency) and shift by 1 to the right (Julia indices)

    # Decode the decision variables into a program tree of MatchNode's:
    program_tree = decode(parent, rule)

    # Convert the MatchNode program tree into a Julia expression
    program = matchnode2expr(program_tree, grammar)

    return program
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
        elseif rule isa Symbol || rule isa Int
            push!(rulenames, string(rule))
        else
            push!(rulenames, string(i))
        end
    end
    #constraints = map(translateConstraint, grammar.constraints)
    return (ruletypes, childtypes, map(string, typenames), rulenames)
end

function decode(parent::Vector{Int}, rule::Vector{Int})::MatchNode
    N = length(parent) + 1
    root_id = N # Last node (outside the range of parent array) is the root
    child_nodes = collect(1:(N-1))
    parental_map = collect(zip(parent, child_nodes))

    program_tree = build_tree(root_id, parental_map, rule)

    return program_tree
end

function build_tree(node_id::Int, parental_map::Vector{Tuple{Int, Int}}, rule::Vector{Int})::MatchNode
    children_ids = Int[]
    
    for (p_i, i) ∈ parental_map
        if (p_i == node_id)
            push!(children_ids, i)
        end
    end
    
    children = map(child_id -> build_tree(child_id, parental_map, rule), children_ids)

    return MatchNode(rule[node_id], children)
end
