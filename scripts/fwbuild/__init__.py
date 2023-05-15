import pathlib
import sys
from .cxx_target import cxx_target
from .toolchains.gcc import gcc

srcdir = pathlib.Path(sys.modules["__main__"].__file__).parent
if srcdir.samefile(pathlib.Path.cwd()):
    outdir = pathlib.Path("bin/")
else:
    outdir = pathlib.Path(".")

# TODO: temporary
from .ninja_syntax import Writer as NinjaWriter
