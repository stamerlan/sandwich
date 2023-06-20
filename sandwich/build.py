import fwbuild
import sandwich.sched.build
import sandwich.spinlock.build

@fwbuild.target
class sandwich(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        self.submodule("sched")
        self.submodule("spinlock")
