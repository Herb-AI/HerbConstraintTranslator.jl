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