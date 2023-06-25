import Pkg

Pkg.add("PyCall")

using PyCall

Base.run(`$(PyCall.python) -m pip install cpmpy matplotlib networkx`)
Base.run(`$(PyCall.python) -m pip install HerbConstraintTranslator.jl\\src\\pyprogtree`)
