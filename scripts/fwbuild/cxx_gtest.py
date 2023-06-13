from .caller import caller
from .cxx_app import cxx_app
from .kconfig import kconfig
import pathlib

class cxx_gtest(cxx_app):
    """ Base class C++ test application which uses google test framework """

    def __init__(self, conf: kconfig, toolchain, name: str | None = None,
                 srcdir: str | pathlib.Path | None = None):
        super().__init__(conf, toolchain, name, srcdir or caller().dir)
        self.default = False
        # TODO: Check if libgtest present
        self.ldlibs += "gtest"
