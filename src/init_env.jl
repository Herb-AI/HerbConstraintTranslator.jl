# A series of bash comands to set up the python environment.

# Base.run(`pwd`)
# Base.run(`$(PyCall.python) -m pip list`)
Base.run(`$(PyCall.python) -m pip install cpmpy matplotlib networkx`) # A better way may be to have an explicit requirements.txt file
Base.run(`$(PyCall.python) -m pip install HerbConstraintTranslator.jl\\src\\pyprogtree`) # Not sure how this would work in general, since the path is relative to the root module Herb.jl
