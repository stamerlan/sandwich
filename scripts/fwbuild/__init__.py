from .cxx_app import cxx_app
from .cxx_module import cxx_module
from .file_set import file_set
from .kconfig import kconfig
from .target import target, targets
from .tool import tool
from .toolchain import toolchain
import contextlib
import os
import pathlib
import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

# Top source directory. The directory where configuration script located
topdir = pathlib.Path(sys.modules["__main__"].__file__).parent

# Configuration script dependencies. Changes in those files trigger invoking
# configuration script before the build.
deps = file_set(topdir, sys.modules["__main__"].__file__)
for root, dirs, files in os.walk(pathlib.Path(__file__).parent):
    for file in files:
        deps.add(pathlib.Path(root, file))
    with contextlib.suppress(ValueError):
        dirs.remove("__pycache__")
