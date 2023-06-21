include("../../HerbGrammar.jl/src/HerbGrammar.jl")
include("../../HerbConstraints.jl/src/HerbConstraints.jl")
include("../../HerbData.jl/src/HerbData.jl")
include("../../HerbEvaluation.jl/src/HerbEvaluation.jl")
include("../../HerbSearch.jl/src/HerbSearch.jl")
include("../../HerbConstraintTranslator.jl/src/HerbConstraintTranslator.jl")

using .HerbGrammar
using .HerbConstraints
using .HerbData
using .HerbEvaluation
using .HerbSearch
using .HerbConstraintTranslator

using Plots

# -- Utilities --:

# Create aliases for Herb constraints:
TopDownOrdered = ComesAfter
TopDownForbidden = ForbiddenPath
LeftRightOrdered = RequireOnLeft

function get_solutions_herb(g::Grammar, max_depth::Int, max_nodes::Int, ret_type::Any)::Vector{Tuple{Any, Float64}}
    iter_herb = get_bfs_enumerator(g, max_depth, max_nodes, ret_type)

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
function enumerate_herb_solutions(g::Grammar; max_depth::Int, max_nodes::Int)::Vector{Tuple{Any, Float64}}
    solutions_herb = Any[]
    ret_types = collect(keys(g.bytype)) # get all unique return types (LHS) in the grammar
    for ret_type in ret_types
        solutions_per_type = get_solutions_herb(g, max_depth, max_nodes, ret_type)
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
function show_all_solutions(solutions_cpmpy::Vector{Tuple{Any, Float64}}, solutions_herb::Vector{Tuple{Any, Float64}})
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

function plot_all_solutions(experiment::String, solutions_cpmpy::Vector{Tuple{Any, Float64}}, solutions_herb::Vector{Tuple{Any, Float64}})
    programs_cpmpy, time_cpmpy = unzip(solutions_cpmpy)
    programs_herb, time_herb = unzip(solutions_herb)

    time_cpmpy_cum = cumsum(time_cpmpy)
    time_herb_cum = cumsum(time_herb)

    N = length(programs_cpmpy)
    M = length(programs_herb)
    if N == M
        # Plot time taken per solution:
        plot(range(1, N), time_cpmpy, label="CPMpy")
        final_plot = plot!(range(1, M), time_herb, label="Herb")
        final_plot = plot(final_plot, xlabel="#Programs", ylabel="Time", title=string("Time Taken per Solution", " (", experiment, ")"))
        # savefig(final_plot, "time_taken_per_solution.png")
        display(final_plot)

        # Plot cumulative time taken:
        plot(range(1, N), time_cpmpy_cum, label="CPMpy")
        final_plot = plot!(range(1, M), time_herb_cum, label="Herb")
        final_plot = plot(final_plot, xlabel="#Programs", ylabel="Time", title=string("Cumulative Time Taken", " (", experiment, ")"))
        # savefig(final_plot, "cumulative_time_taken.png")
        display(final_plot)
    else
        println("The number of enumerated programs is different. CPMpy found ", N, " programs, while Herb found ", M, " programs.")
    end
end

function benchmark(experiment::String, g::Grammar; max_nodes::Int, max_depth::Int, solution_limit::Int, plot_solutions::Bool)    
    solutions_cpmpy = enumerate_cpmpy_solutions(g, max_nodes=max_nodes, max_depth=max_depth, solution_limit=solution_limit, plot_solutions=plot_solutions)
    solutions_herb = enumerate_herb_solutions(g, max_depth=max_depth, max_nodes=max_nodes)
    
    # show_all_solutions(solutions_cpmpy, solutions_herb)
    plot_all_solutions(experiment, solutions_cpmpy[2:end], solutions_herb[2:end])
end


# -- Experiments --:

g = HerbGrammar.@csgrammar begin
    Real = |(0:1)               #1/2
    Real = Bool ? Real : Real   #3
    Real = Sqrt(Real)           #4
    Bool = Not(Bool)            #5
    Bool = Bool && Bool         #6
    Real = Real + Real          #7
    Bool = Real >= Real         #8
    Bool = T                    #9
    Bool = F                    #10
end

function experiment_1(g::Grammar)
    println("-- Experiment 1 (unconstrained cfg) --")
    experiment = "Experiment 1"

    max_nodes = 4
    max_depth = 4
    solution_limit = typemax(Int)
    plot_solutions = false
    
    benchmark(experiment, g, max_nodes=max_nodes, max_depth=max_depth, solution_limit=solution_limit, plot_solutions=plot_solutions)
end
function experiment_2(g::Grammar)
    println("-- Experiment 2 (forbidden symmetry) --")
    experiment = "Experiment 2"

    constraint = Forbidden(
        MatchNode(7, [MatchVar(:x), MatchVar(:x)])
    )

    addconstraint!(g, constraint)

    max_nodes = 4
    max_depth = 4
    solution_limit = typemax(Int)
    plot_solutions = false

    benchmark(experiment, g, max_nodes=max_nodes, max_depth=max_depth, solution_limit=solution_limit, plot_solutions=plot_solutions)
end
function experiment_3(g::Grammar)
    println("-- Experiment 3 (permutation of constraints) --")
    experiment = "Experiment 3"

    constraints = [
        [
            TopDownOrdered(1, [4]),
            TopDownOrdered(9, [3, 6])
        ],
        [
            TopDownForbidden([4,4]),
            TopDownForbidden([6,10])
        ],
        [
            LeftRightOrdered([4, 1]),
            LeftRightOrdered([1, 2])
        ],
        [
            Ordered(MatchNode(6, [MatchVar(:x), MatchVar(:y)]), [:x, :y]),
            Ordered(MatchNode(7, [MatchVar(:x), MatchVar(:y)]), [:x, :y])
        ],
        [
            Forbidden(MatchNode(3, [MatchVar(:x), MatchVar(:y), MatchVar(:y)])),
            Forbidden(MatchNode(6, [MatchVar(:x), MatchVar(:x)])),
            Forbidden(MatchNode(8, [MatchVar(:x), MatchVar(:x)])),
            Forbidden(MatchNode(5, [MatchNode(5)]))
        ]
    ]

    for (i, cs₁) ∈ enumerate(constraints)
        for cs₂ ∈ constraints[i+1:end]
            g.constraints = Constraint[]
            foreach(cs₁) do c addconstraint!(g, c) end
            foreach(cs₂) do c addconstraint!(g, c) end
        end
    end
    
    max_nodes = 4
    max_depth = 4
    solution_limit = typemax(Int)
    plot_solutions = false

    benchmark(experiment, g, max_nodes=max_nodes, max_depth=max_depth, solution_limit=solution_limit, plot_solutions=plot_solutions)
end

# Run all experiments:
experiments = [experiment_1, experiment_2, experiment_3]
foreach(e -> e(g), experiments)
