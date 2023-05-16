import importlib
import pathlib
import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

# Setup default srcdir and outdir
srcdir = pathlib.Path(sys.modules["__main__"].__file__).parent
if srcdir.samefile(pathlib.Path.cwd()):
    outdir = pathlib.Path("bin/")
else:
    outdir = pathlib.Path(".")

# Target platform module
platform = importlib.import_module(".platform-none", __name__)
