import sys
# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

from .cxx_app import cxx_app
from .cxx_gtest import cxx_gtest
from .cxx_module import cxx_module
from .kconfig import kconfig
from .ninja import ninja, ninja_writer
from .build import build, build_cls
from .mkpath import mkpath, relative_path
from .shellcmd import shellcmd
from .tool import tool
from .toolchain import toolchain
from pathlib import Path
import contextlib
import os

# Top source directory. The directory where configuration script located
topdir = Path(sys.modules["__main__"].__file__).parent

# Configuration script dependencies. Changes in those files trigger invoking
# configuration script before the build.
deps: set[Path] = set([Path(sys.modules["__main__"].__file__)])
for root, dirs, files in os.walk(Path(__file__).parent):
    for file in files:
        deps.add(Path(root, file))
    with contextlib.suppress(ValueError):
        dirs.remove("__pycache__")
