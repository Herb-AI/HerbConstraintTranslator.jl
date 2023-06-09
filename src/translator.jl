# Import the python utilities:

py"""
from pyprogtree import runner
from pyprogtree.match_node import MatchNode
"""

GrammarEncoding = Tuple{Vector{Int}, Vector{Vector{Int}}, Vector{String}, Vector{String}}
TimedResults = Tuple{Vector{Any}, Vector{Real}, Real}

rule_count = 0

function solve(
    grammar::ContextSensitiveGrammar;
    min_nodes::Int=1, max_nodes::Int=15, max_depth::Int=4, return_type::Union{Int, Nothing}=nothing, 
    solution_limit::Union{Int, Nothing}=1, plot_solutions::Bool=false
)::TimedResults
    global rule_count = length(grammar.rules)
    
    if return_type !== nothing 
        return_type -= 1
    end

    # Encode the grammar:
    ruletypes, childtypes, typenames, rulenames = translate(grammar)
    constraints = map(translate_constraint, grammar.constraints)

    # Solve and obtain decision variables: list of (parent, rule) tuples
    results, ind_times, enum_time = py"runner.run"(
        ruletypes, childtypes, typenames, rulenames, constraints, 
        min_nodes, max_nodes, max_depth, return_type, solution_limit, plot_solutions
    )
    
    programs = Any[]
    for (parent, rule) ∈ results
        parent = map(p -> convert(Int64, p) + 1, parent) # Convert from Int32 to Int64 (for consistency) and shift by 1 to the right (Julia indices)
        rule = map(r -> convert(Int64, r) + 1, rule) # Convert from Int32 to Int64 (for consistency) and shift by 1 to the right (Julia indices)

        # Decode the decision variables into a program tree of MatchNode's:
        program_tree = decode(parent, rule)

        # Convert the MatchNode program tree into a Julia expression and add to programs
        push!(programs, matchnode2expr(program_tree, grammar))
    end

    return programs, ind_times, enum_time
end

guarded_reindex(i::Int)::Int = 0 < i ≤ rule_count ? i - 1 : error("rule $(i) out of bounds")

function translate_match_node(node::AbstractMatchNode, path::Union{Vector{Int}, Nothing}=nothing)::PyObject
    if node isa MatchNode
        idx = guarded_reindex(node.rule_ind)
        children = map(translate_match_node, node.children)
        py"MatchNode"(idx, children, path)
    elseif node isa MatchVar
        py"MatchNode"(string(node.var_name))
    else
        error("Didn't expect $(typeof(node))!")
    end
end

function translate_constraint(c::Constraint)::Tuple{String, Any}
    if c isa ForbiddenPath
        ("TDF", map(guarded_reindex, deepcopy(c.sequence)))
    elseif c isa ComesAfter
        ("TDO", map(guarded_reindex, push!(deepcopy(c.predecessors), c.rule)))
    elseif c isa RequireOnLeft
        ("LRO", map(guarded_reindex, deepcopy(c.order)))
    elseif c isa Ordered
        ("O", [translate_match_node(c.tree), map(string, c.order)])
    elseif c isa LocalOrdered
        ("LO", [translate_match_node(c.tree, c.path), map(string, c.order)])
    elseif c isa Forbidden
        ("F", translate_match_node(c.tree))
    elseif c isa LocalForbidden
        ("LF", translate_match_node(c.tree, c.path))
    else
        error("$(typeof(c)) is unsupported!")
    end
end

function translate(grammar::ContextSensitiveGrammar)::GrammarEncoding
    typenames  = reverse(collect(keys(grammar.bytype)))
    typeindex  = Dict(zip(typenames, 0:length(typenames)-1))
    # rename type symbols with their indeces
    ruletypes  = map(t -> typeindex[t], grammar.types)
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
            push!(rulenames, string("rule#", i))
        end
    end
    
    return (ruletypes, childtypes, map(string, typenames), rulenames)
end

function decode(parent::Vector{Int}, rule::Vector{Int})::MatchNode
    N = length(parent) + 1
    root_id = N # Last node (outside the range of parent array) is the root
    child_nodes = collect(1:(N-1))
    parental_map = reverse!(collect(zip(parent, child_nodes)))

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
