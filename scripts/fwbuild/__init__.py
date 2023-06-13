from .cxx_app import cxx_app
from .kconfig import kconfig
from .target import target
import pathlib
import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

# Top source directory. The directory where configuration script located
topdir = pathlib.Path(sys.modules["__main__"].__file__).parent
