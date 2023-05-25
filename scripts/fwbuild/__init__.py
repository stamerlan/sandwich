from .include import include
from .kconfig import kconfig, write_autoconf
from argparse import Namespace
import pathlib
import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

# Setup top source directory and top output directory
topdir = pathlib.Path(sys.modules["__main__"].__file__).parent
if topdir.samefile(pathlib.Path.cwd()):
    topout = pathlib.Path("bin/")
else:
    topout = pathlib.Path(".")

# Set of files used during configuration. If any file in the list changed
# configure script has to be run again.
# Each path is either absolute or relative to fwbuild.topdir and starts with
# $topdir.
conf_files: set[str] = set()

def add_conf_file(filename: str | pathlib.Path):
    filename = pathlib.Path(filename)
    if filename.is_relative_to(topdir):
        filename = pathlib.Path("$topdir", filename.relative_to(topdir))
    conf_files.add(filename.as_posix())

# Add this file and include.py to conf_files
add_conf_file(__file__)
add_conf_file(pathlib.Path(__file__).parent / "include.py")
add_conf_file(pathlib.Path(__file__).parent / "kconfig.py")

# Target platform module
platform = include("platform-none.py", "fwbuild.platform.none")

# Configuration symbols loaded by fwbuild.kconfig()
conf = Namespace()
