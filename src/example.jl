module example

#= This module demonstrates the basic usage of HerbConstraintTranslator =#

include("../../src/Herb.jl")

using .Herb.HerbConstraintTranslator
using .Herb.HerbConstraints
using .Herb.HerbGrammar

g = HerbGrammar.@csgrammar begin
    Var  = x                #1
    Term = Var              #2
    Term = Lam(Var, Term)   #3
    Term = App(Term, Term)  #4
end

constraints = [
    # only allow x if its bound
    ComesAfter(1, [3])

    # forbid fixpoint (λ x. x x) (λ x. x x)
    Forbidden(MatchNode(4, [
        MatchNode(3, [MatchNode(1), MatchNode(4, [MatchNode(1), MatchNode(1)])]), 
        MatchNode(3, [MatchNode(1), MatchNode(4, [MatchNode(1), MatchNode(1)])])
    ]))
]

foreach(constraints) do c 
    addconstraint!(g, c)
end

# take the result, ignoring timing information
results, _, _ = HerbConstraintTranslator.solve(
    g, min_nodes=2, max_nodes=8, max_depth=4, return_type=2, solution_limit=4
)

println.(results)

end # module


module experiments

#= This is how to run our experiments =#

include("../../src/Herb.jl")

using .Herb.HerbConstraintTranslator

HerbConstraintTranslator.run_experiments()

end # module