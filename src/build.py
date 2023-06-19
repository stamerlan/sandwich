import fwbuild

# TODO: Flags are defined for GCC toolchain only
@fwbuild.build
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

        self.ldflags += "-flto", "-g"

        self.submodule("drivers")
        self.submodule("sandwich")

        self.src("main.cc")
