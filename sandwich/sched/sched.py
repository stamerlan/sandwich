import fwbuild
import fwbuild.targets

class sched(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app):
        super().__init__("sched", target)

        target.include(fwbuild.this_dir / "include")

        self.src("src/sched.cc")

test = fwbuild.platform.cxx_gtest("sched_test")
test.include(fwbuild.this_dir / "include")
test.src("src/sched.cc")
test.src("tests/sched_test.cc")
test.ldlibs += "gtest_main"
