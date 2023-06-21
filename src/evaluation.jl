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
    size = 1 + sum(zip(expr.args, bases), init=0) do (arg, base)
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

function find_diff(ours, theirs)
    fst = (pair) -> pair[1]

    extras = fst.(filter(collect(enumerate(ours))) do (i, p)
        p ∉ theirs
    end)

    missed = fst.(filter(collect(enumerate(theirs))) do (i, p)
        p ∉ ours
    end)

    (extras, missed)
end

function eval(
    g::ContextSensitiveGrammar, max_nodes::Int, max_depth::Int;
    print_to_file=true, break_symm=false, run_ours=true, label::Union{String, Nothing}=nothing
)
    outputln = if print_to_file
        file = open("eval.txt", "a")
        function (args...)
            write(file, map(string, args)..., "\n")
        end
    else println end

    outputln(if label !== nothing "\n====$(label)====" else "\n=======================" end) 
    
    herb_results = @time append!(collect(
        HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, :Real)),
        HerbSearch.get_bfs_enumerator(g, max_depth, max_nodes, :Bool))
    herb_results = map(herb_results) do node
        HerbGrammar.rulenode2expr(node, g)
    end

    outputln("herb found $(length(herb_results)) solutions")

    if run_ours
        our_results = HerbConstraintTranslator.solve(
            g, min_nodes=1, max_nodes=max_nodes, max_depth=max_depth, solution_limit=nothing, plot_solutions=false
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
            outputln("$(length(type_errors)) solutions don't typecheck:\n")
            foreach(outputln, type_errors)
        end

        if break_symm 
            our_original = deepcopy(our_results)
            herb_original = deepcopy(herb_results)
            HerbConstraintTranslator.canonicalize!.(our_results)
            HerbConstraintTranslator.canonicalize!.(herb_results)

            count = 0
            for (i, p₁) ∈ enumerate(our_results)
                for (j, p₂) ∈ Iterators.reverse(enumerate(our_results[i+1:end]))
                    if p₁ == p₂
                        count += 1
                        if count == 1 
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

        added, missed = HerbConstraintTranslator.find_diff(our_results, herb_results)

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
end