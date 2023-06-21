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

# Tests:

# Redefinition of operators to prevent Julia from assuming commutativity when printing
+(a, b) = a + b
*(a, b) = a * b
-(a, b) = a - b

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

constraint = Forbidden(
    MatchNode(7, [MatchVar(:x), MatchVar(:x)])
)
addconstraint!(g, constraint)

"""
Size comparison between CPMpy model solution set and Herb enumeration
"""
function test_1(g::Grammar)
    println("-- Test 1 --")
    cpmpy_programs = @time HerbConstraintTranslator.solve(g, max_nodes=5, max_depth=4, solution_limit=5, plot_solutions=false)
    @show size(cpmpy_programs)

    herb_programs1 = @time collect(get_bfs_enumerator(g, 5, 5, :Real))
    herb_programs2 = @time collect(get_bfs_enumerator(g, 5, 5, :Bool))
    herb_programs = vcat(herb_programs1, herb_programs2)
    @show size(herb_programs)
end

"""
Timing of the CPMpy model search for individual programs
"""
function test_2(g::Grammar)
    println("-- Test 2 --")
    cpmpy_programs = @time HerbConstraintTranslator.solve(g, max_nodes=5, max_depth=4, solution_limit=10, plot_solutions=false)
    for (program, time) ∈ cpmpy_programs
        println("Time taken: ", time)
    end
end

# Run all tests:
tests = [test_2]
foreach(e -> e(g), tests)
