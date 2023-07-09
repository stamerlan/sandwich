import fwbuild
import src.display.build

# TODO: Flags are defined for GCC toolchain only
@fwbuild.target
class hello(fwbuild.cxx_app):
    def __init__(self, conf: fwbuild.kconfig, toolchain: fwbuild.toolchain):
        super().__init__(conf, toolchain)

        self.disassembly = True
        self.mapfile = True

        self.include(".")

        self.cxxflags += "-std=c++23", "-g", "-O3"
        self.cxxflags += "-fcheck-new", "-flto", "-fno-rtti", "-fno-exceptions"
        self.cxxflags += "-fno-threadsafe-statics"
        self.cxxflags += "-Wall", "-Wextra", "-Werror", "-Weffc++"
        self.cxxflags += "-Wmultiple-inheritance", "-Wvirtual-inheritance"
        self.cxxflags += "-ffile-prefix-map=$topdir/="

        self.ldflags += "-flto", "-g"

        self.submodule("arch")
        self.submodule("drivers")
        self.submodule("sandwich")
        self.submodule("display")

        self.src("main.cc")
