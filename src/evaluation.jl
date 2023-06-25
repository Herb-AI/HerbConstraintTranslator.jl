const output_filename = "timing.txt"
const error_filename  = "err.txt"    

@enum Type TInt=1 TBool=2

Term = Union{Expr, Symbol, Int}

struct TypeCheckError <: Exception
    msg::String
end

function expect(expr::Term, type::Type)::Type
    if typecheck(expr) == type
        return TBool
    else
        throw(TypeCheckError("expected $(expr) to be a $(type) expression!"))
    end
end

function expect(this::Type, other::Type)::Type
    if this == other
        return this
    else
        throw(TypeCheckError("expected $(expr) to be a $(type) expression!"))
    end
end

function checkop(op::Symbol, args::Term...)::Type
    if op == :+
        expect(unify(args[1], args[2]), TInt)
    elseif op == :>=
        expect(unify(args[1], args[2]), TInt)
        TBool
    elseif op == :&&
        expect(unify(args[1], args[2]), TBool)
    elseif op == :Not
        expect(typecheck(args[1]), TBool)
    elseif op == :Sqrt
        expect(typecheck(args[1]), TInt)
    end
end

function unify(expr₁::Term, expr₂::Term)::Type
    t = typecheck(expr₁)
    if t == typecheck(expr₂)
        return t
    else
        throw(TypeCheckError("expected $(expr₁) and $(expr₂) to be of the same type"))
    end
end

extract_block(t::Term)::Term = t isa Expr ? t.args[2] : t

function typecheck(expr::Term)::Type
    if expr isa Expr
        if expr.head == :call
            op   = expr.args[1]
            args = expr.args[2:end]
            checkop(op, args...)
        elseif expr.head == :if
            cond, tblock, eblock = expr.args
            tbranch, ebranch = extract_block(tblock), extract_block(eblock)
            expect(cond, TBool)
            unify(tbranch, ebranch)
        else
            checkop(expr.head, expr.args...)
        end
    elseif expr == :T || expr == :F
        return TBool
    elseif expr isa Int
        return TInt
    end
end

struct DecoratedTerm
    expr::Term
    size::Int
end

extract_decorated_block(t::DecoratedTerm)::DecoratedTerm = t.expr isa Expr ? t.expr.args[2] : t

function strip!(expr::Expr)::Expr
    map!(expr.args, expr.args) do arg
        if arg isa Expr && arg.head == :block
            if arg.args[1] isa LineNumberNode
                deleteat!(arg.args, 1)
            end
            if length(arg.args) == 1
                return arg.args[1]
            end
        end
        return arg
    end
    for arg ∈ expr.args
        if arg isa Expr strip!(arg) end
    end
    return expr
end

function decorate!(expr::Term)::DecoratedTerm
    if !(expr isa Expr) return DecoratedTerm(expr, sum(Int, string(expr))) end
    expr.args = decorate!.(expr.args)
    bases = [5 ^ i for i ∈ 0:length(expr.args)]
    size = sum(zip(expr.args, bases), init=0) do (arg, base)
        arg.size * base
    end
    return DecoratedTerm(expr, size)
end

function undecorate!(a::DecoratedTerm)::Term
    expr = a.expr
    if expr isa Expr
        expr.args = undecorate!.(expr.args)
    end
    return expr
end

function canonicalize_decorated!(a::DecoratedTerm)::DecoratedTerm
    expr = a.expr
    if expr isa Expr
        args = expr.args
        if (args[1].expr == :+) && args[2].size > args[3].size
            expr.args[2:3] = reverse(expr.args[2:3])
        elseif (expr.head == :&&) && args[1].size > args[2].size
            reverse!(expr.args)
        end
        canonicalize_decorated!.(args)
    end
    return a
end

function canonicalize!(expr::Term)::Term
    if expr isa Expr strip!(expr) end
    a = decorate!(expr)
    a = canonicalize_decorated!(a)
    undecorate!(a)
end

function diff_args(ours, theirs)
    extras = first.(filter(collect(enumerate(ours))) do (i, p)
        p ∉ theirs
    end)

    missed = first.(filter(collect(enumerate(theirs))) do (i, p)
        p ∉ ours
    end)
    
    (extras, missed)
end

function eval(
    g::ContextSensitiveGrammar, max_nodes::Int, max_depth::Int, return_type::Union{Int, Nothing}=nothing;
    break_symm=false, compare_with_herb=true, enum=true,
    filename="eval.txt", label=nothing
)
    failed = false
    print_to_file = filename !== nothing
    outputln = if print_to_file
        file = open(filename, "a")
        function (args...)
            write(file, map(string, args)..., "\n")
        end
    else println end

    header = if label !== nothing "\n====$(label)====" else "\n=======================" end

    if print_to_file outputln(header) end

    println(header)

    herb_time = nothing
    if compare_with_herb
        start_time = time()
        if return_type !== nothing
            ret = return_type == 1 ? :Real : :Bool
            herb_results = collect(HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, ret))
        else
            herb_results = append!(collect(
                HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, :Real)),
                HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, :Bool))
        end
        herb_time = time() - start_time
        println("Herb took $(herb_time)")
        
        herb_results = map(herb_results) do node
            HerbGrammar.rulenode2expr(node, g)
        end

        outputln("Herb found $(length(herb_results)) solutions")
    end

    solution_limit = enum ? nothing : 1
    our_results, ind_times, enum_time = HerbConstraintTranslator.solve(
        g, min_nodes=1, max_nodes=max_nodes, max_depth=max_depth, return_type=return_type, 
        solution_limit=solution_limit, plot_solutions=false
    )

    outputln("We took $(enum_time)")
    outputln("we found $(length(our_results)) solutions")

    type_errors = filter(our_results) do expr
        try
            HerbConstraintTranslator.typecheck(expr)
            return false
        catch err
            if err isa TypeCheckError return true else throw(err) end
        end
    end

    if length(type_errors) > 0
        failed = true
        outputln("$(length(type_errors)) solutions don't typecheck:\n")
        foreach(outputln, type_errors)
    end

    # find duplicates up to commutativity of `+` and `&&` enforced by Ordered constraints
    if break_symm && enum
        our_original = deepcopy(our_results)
        HerbConstraintTranslator.canonicalize!.(our_results)

        count = 0
        for (i, p₁) ∈ enumerate(our_results)
            for (j, p₂) ∈ enumerate(our_results[i+1:end])
                if p₁ == p₂
                    count += 1
                    if count == 1
                        failed = true
                        outputln("\nOur duplicate solutions after canonicalization:\n") 
                    end
                    outputln("-----------\n", p₁, "\n")
                    outputln("originals:")
                    outputln(our_original[i])
                    outputln(our_original[i+j])
                    outputln()
                end
            end
        end
        if count > 0 outputln("$(count) total duplicates") end
    end

    if compare_with_herb && enum
        if break_symm
            herb_original = deepcopy(herb_results)
            HerbConstraintTranslator.canonicalize!.(herb_results)
        end
        
        added, missed = HerbConstraintTranslator.diff_args(our_results, herb_results)

        failed |= !(length(added) == length(missed) == 0)

        if break_symm
            outputln("\n$(length(added)) superfluous programs:\n")
            outputln.(our_original[added], "\n")
            outputln("\n$(length(missed)) missing programs:\n")
            outputln.(herb_original[missed], "\n")
        else
            outputln("\n$(length(added)) superfluous programs:\n")
            outputln.(our_results[added], "\n")
            outputln("\n$(length(missed)) missing programs:\n")
            outputln.(herb_results[missed], "\n")
        end
    end

    if print_to_file 
        close(file)
    end

    if failed error("sanity checks failed!") end    

    return ind_times, enum_time, herb_time, length(our_results)
end

function runWith(max_nodes, max_depth, ret, enum, run_herb=true, css...)
    g.constraints = append!(Constraint[], css...)
    break_symm = any(isa.(first.(css), Ordered))
    label = join(replace.(
                css .|> first .|> typeof .|> string, 
                r".*\.Herb.HerbConstraints\."=>""), ", ")
    label = label == "" ? "NoConstraints" : label
    quant = enum ? "enum" : "one"
    return_type = ret === nothing ? "None" : ret == 1 ? "Real" : "Bool"
    lines::Vector{Any} = [  
        label, 
        "$(max_nodes), $(max_depth)", 
        return_type,
        quant
    ]
    try
        _, our_time, herb_time, count = eval(
            g, max_nodes, max_depth, ret,
            enum=enum, compare_with_herb=run_herb, break_symm=break_symm, label=label, filename=nothing
        )
        push!(lines, herb_time, count, our_time)
        out_file = open(output_filename, "a")
        write(out_file, join(string.(lines) .* "\n"), "\n")
        close(out_file)
    catch err
        push!(lines, err)
        err_file = open(error_filename, "a")
        write(err_file, join(string.(lines) .* "\n"), "\n")
        close(err_file)
    end
end

TopDownOrdered = ComesAfter
TopDownForbidden = ForbiddenPath
LeftRightOrdered = RequireOnLeft

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

constraints = [
    [
        TopDownOrdered(1, [4]),
        TopDownOrdered(9, [3, 6])
    ],
    [
        TopDownForbidden([4, 4]),
        TopDownForbidden([6, 10]),
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
        Forbidden(MatchNode(5, [MatchNode(5)]))
    ]
]

#=
    Prints the timing results into `output_filename` and 
    any errors that might occur into `error_filename`.
    Timing for a single run is formatted as follows:
    
    ConstraintType₁,..., ConstraintTypeₙ
    max_node, max_depth
    return_type
    one | enum
    herb_time
    solution_count
    cpmpy_time

    Each run is separated by double new line.
=#
function run_experiments()
    max_depth = 4
    for max_nodes ∈ [4, 5, 6, 7], enum ∈ [false, true]
        ret = enum ? nothing : 1
        # each constraint by itself
        for cs ∈ constraints
            runWith(max_nodes, max_depth, ret, enum, true, cs)
        end
        # all pairs
        for (i, cs₁) ∈ enumerate(constraints)
            for cs₂ ∈ constraints[i+1:end]
                runWith(max_nodes, max_depth, ret, enum, true, cs₁, cs₂)
            end
        end
        # all toghether
        runWith(max_nodes, max_depth, ret, enum, true, constraints...)
    end
end