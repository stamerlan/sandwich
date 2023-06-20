import fwbuild

@fwbuild.target
class sched(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        target.include("include")
        self.src("src/sched.cc")

@fwbuild.target
class sched_test(fwbuild.cxx_gtest):
    def __init__(self, conf: fwbuild.kconfig, toolchain: fwbuild.toolchain):
        super().__init__(conf, toolchain)
        self.include("include")

        self.cxxflags += "-g"

        self.ldlibs += "gtest_main"

        self.src("src/sched.cc")
        self.src("tests/sched_test.cc")
