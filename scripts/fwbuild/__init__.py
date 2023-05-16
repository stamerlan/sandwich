import pathlib
import sys
from .cxx_target import cxx_target
from .toolchains.gcc import gcc

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

# Setup default srcdir and outdir
srcdir = pathlib.Path(sys.modules["__main__"].__file__).parent
if srcdir.samefile(pathlib.Path.cwd()):
    outdir = pathlib.Path("bin/")
else:
    outdir = pathlib.Path(".")

# TODO: temporary
from .ninja_syntax import Writer as NinjaWriter
