import fwbuild
import sandwich.sched.build

@fwbuild.build
class sandwich(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)

        target.include("include")

        self.submodule("sched")
