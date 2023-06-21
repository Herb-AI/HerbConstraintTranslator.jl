include("../../HerbGrammar.jl/src/HerbGrammar.jl")
include("../../HerbConstraints.jl/src/HerbConstraints.jl")
include("../../HerbConstraintTranslator.jl/src/HerbConstraintTranslator.jl")
include("../../HerbData.jl/src/HerbData.jl")
include("../../HerbEvaluation.jl/src/HerbEvaluation.jl")
include("../../HerbSearch.jl/src/HerbSearch.jl")

using .HerbGrammar
using .HerbConstraints
using .HerbConstraintTranslator
using .HerbData
using .HerbEvaluation
using .HerbSearch

using Plots

# -- Utilities --:

function get_solutions_herb(g::Grammar, max_depth::Int, max_size::Int, ret_type::Any)::Vector{Tuple{Any, Float64}}
    iter_herb = get_bfs_enumerator(g, max_depth, max_size, ret_type)

    solutions = Any[]

    # Time the initial program:
    start_time = time()
    next = iterate(iter_herb)

    # Enumerate and time the rest of the programs:
    while next !== nothing
        (program, state) = next
        end_time = time()
        time_elapsed = end_time - start_time
        push!(solutions, (rulenode2expr(program, g), time_elapsed))

        start_time = time()
        next = iterate(iter_herb, state)
    end
    
    return solutions
end
function enumerate_herb_solutions(g::Grammar; max_depth::Int, max_size::Int)::Vector{Tuple{Any, Float64}}
    solutions_herb = Any[]
    ret_types = collect(keys(g.bytype)) # get all unique return types (LHS) in the grammar
    for ret_type in ret_types
        solutions_per_type = get_solutions_herb(g, max_depth, max_size, ret_type)
        solutions_herb = vcat(solutions_herb, solutions_per_type)
    end
    return solutions_herb
end

function enumerate_cpmpy_solutions(g::Grammar; max_nodes::Int, max_depth::Int, solution_limit::Int, plot_solutions::Bool)::Vector{Tuple{Any, Float64}}
    return HerbConstraintTranslator.solve(g, max_nodes=max_nodes, max_depth=max_depth, solution_limit=solution_limit, plot_solutions=plot_solutions)
end

function show_solutions(solutions::Vector{Tuple{Any, Float64}})
    for (program, time) ∈ solutions
        println("Program: ", program)
        println("Time taken: ", time)
    end
end
function show_solutions(solutions_cpmpy::Vector{Tuple{Any, Float64}}, solutions_herb::Vector{Tuple{Any, Float64}})
    println("CPMpy Solutions")
    show_solutions(solutions_cpmpy)
    println("------")

    println("Herb Solutions")
    show_solutions(solutions_herb)
    println("------")
end

function fst()
    return ((a, _),) -> a
end
function snd()
    return ((_, b),) -> b
end
function unzip(xs)
    return map(fst(), xs), map(snd(), xs)
end

function plot_solutions(solutions_cpmpy::Vector{Tuple{Any, Float64}}, solutions_herb::Vector{Tuple{Any, Float64}})
    programs_cpmpy, time_cpmpy = unzip(solutions_cpmpy)
    programs_herb, time_herb = unzip(solutions_herb)

    N = length(programs_cpmpy)
    M = length(programs_herb)
    if N == M
        display(plot(range(1, length(programs_cpmpy)), [time_cpmpy, time_herb]))
    else
        println("The number of enumerated programs is different. CPMpy found ", N, " programs, while Herb found ", M, " programs.")
        plot_cpmpy = plot(range(1, length(programs_cpmpy)), time_cpmpy, ylabel="CPMpy")
        plot_herb = plot(range(1, length(programs_herb)), time_herb, ylabel="Herb")
        display(plot(plot_cpmpy, plot_herb))
    end
end

function benchmark(g::Grammar)    
    solutions_cpmpy = enumerate_cpmpy_solutions(g, max_nodes=5, max_depth=4, solution_limit=typemax(Int), plot_solutions=false)
    solutions_herb = enumerate_herb_solutions(g, max_depth=4, max_size=5)
    
    # show_solutions(solutions_cpmpy, solutions_herb)
    plot_solutions(solutions_cpmpy[2:end], solutions_herb[2:end])
end


# -- Experiments --:

# Define a base context-free grammar:
g = HerbGrammar.@csgrammar begin
    Real = |(0:1)
    Real = Bool ? Real : Real
    Real = Sqrt(Real)
    Bool = Not(Bool)
    Bool = Bool && Bool
    Real = Real + Real
    Bool = Real >= Real
    Bool = T
    Bool = F
end

function experiment_1(g::Grammar)
    println("-- Experiment 1 (unconstrained cfg) --")
    benchmark(g)
end
function experiment_2(g::Grammar)
    println("-- Experiment 2 (forbidden symmetry) --")
    constraint = Forbidden(
        MatchNode(7, [MatchVar(:x), MatchVar(:x)])
    )
    addconstraint!(g, constraint)

    benchmark(g)
end

# Run all experiments:
experiments = [experiment_1, experiment_2]
foreach(e -> e(g), experiments)
