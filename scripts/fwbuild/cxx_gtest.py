from .cxx_app import cxx_app
from pathlib import Path
import fwbuild

class cxx_gtest(cxx_app):
    """ Base class C++ test application which uses google test framework """

    def __init__(self, conf: "fwbuild.kconfig", toolchain: "fwbuild.toolchain",
                 name: str | None = None, srcdir: str | Path | None = None):
        super().__init__(conf, toolchain, name, srcdir or fwbuild.caller().dir)
        self.default = False
        # TODO: Check if libgtest present
        self.ldlibs += "gtest"
