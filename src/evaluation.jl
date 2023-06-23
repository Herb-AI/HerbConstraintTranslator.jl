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

function trimTiming(filename::String)::Vector{String}
    text = open(filename) do file
        read(file, String)
    end
    pattern = r"init grammar\nSetting up decision variables... DONE\nSetting up the model... (return type set to [01])?\nDONE\nSolving the model...\n\n"
    blocks = split(replace(text, pattern=>""), "\n\n")
    lineblocks = split.(blocks, "\n")
    deleteat!.(lineblocks, 3)
    blocks = join.(lineblocks, "\n")
end

function eval(
    g::ContextSensitiveGrammar, max_nodes::Int, max_depth::Int, return_type::Union{Int, Nothing}=nothing;
    break_symm=false, compare_with_herb=true, solution_limit=nothing,
    print_to_file=true, label=nothing
)
    outputln = if print_to_file
        file = open("eval.txt", "a")
        function (args...)
            write(file, map(string, args)..., "\n")
        end
    else println end

    failed = false

    header = if label !== nothing "\n====$(label)====" else "\n=======================" end

    if print_to_file
        outputln(header)
    end
    
    println(header)

    if compare_with_herb
        print("Herb took")
        if return_type !== nothing
            ret = reverse(collect(keys(g.bytype)))[return_type]
            herb_results = @time collect(HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, ret))
        else
            herb_results = @time append!(collect(
                HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, :Real)),
                HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, :Bool))
        end
        herb_results = map(herb_results) do node
            HerbGrammar.rulenode2expr(node, g)
        end
    end

    outputln("Herb found $(length(herb_results)) solutions")

    our_results = HerbConstraintTranslator.solve(
        g, min_nodes=1, max_nodes=max_nodes, max_depth=max_depth, return_type=return_type, 
        solution_limit=solution_limit, plot_solutions=false
    )

    if print_to_file outputln("we found $(length(our_results)) solutions") end

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

    if break_symm
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

    if compare_with_herb
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

    if print_to_file close(file) end

    return !failed
end

