import fwbuild

@fwbuild.build
class sched(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        target.include("include")
        self.src("src/sched.cc")

@fwbuild.build
class sched_test(fwbuild.cxx_gtest):
    def __init__(self, conf: fwbuild.kconfig, toolchain):
        self.include("include")
        self.ldlibs += "gtest_main"

        self.src("src/sched.cc")
        self.src("tests/sched_test.cc")
