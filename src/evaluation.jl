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

function flatten(expr::Term)::Vector{Any}
    if expr isa Expr
        if expr.head == :call
            expr.args
        elseif expr.head == :if
            cond, tblock, eblock = expr.args
            [:if, cond, 
                extract_decorated_block(tblock), 
                extract_decorated_block(eblock)]
        else
            [expr.head, expr.args...]
        end
    elseif expr isa Int || expr isa Symbol
        [expr]
    end
end

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
    extras = filter(ours) do p
        p ∉ theirs
    end

    missed = filter(theirs) do p
        p ∉ ours
    end

    (extras, missed)
end