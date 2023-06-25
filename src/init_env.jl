# replace this with you own conda pyprogtree location
# build_location = "D:\\ProgramData\\Miniconda3\\Lib\\site-packages\\pyprogtree\\"

# A series of bash comands to set up the python environment.
Base.run(`$(PyCall.python) -m pip uninstall -y pyprogtree`) # the last line should be enough now 
Base.run(`$(PyCall.python) -m pip install --upgrade --force-reinstall  HerbConstraintTranslator.jl\\src\\pyprogtree`) # Not sure how this would work in general, since the path is relative to the root module Herb.jl
# Base.run(`xcopy .\\HerbConstraintTranslator.jl\\src\\pyprogtree\\pyprogtree\\ $(build_location) /E /C /H /R /K /O /Y`)
