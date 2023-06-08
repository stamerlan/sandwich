import fwbuild
import fwbuild.targets

class sandwich(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app):
        super().__init__("sandwich", target)

        self.submodule("sched")
