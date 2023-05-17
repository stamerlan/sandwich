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

# Set of files used during configuration. Each path is either absolute or
# relative to fwbuild.srcdir and starts with $topsrcdir and is
conf_files: set[str] = set()

def add_conf_file(filename: str | pathlib.Path):
    filename = pathlib.Path(filename)
    if filename.is_relative_to(srcdir):
        filename = pathlib.Path("$topsrcdir", filename.relative_to(srcdir))
    conf_files.add(filename.as_posix())
