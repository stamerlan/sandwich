import fwbuild
import fwbuild.targets

class drivers(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app):
        super().__init__("drivers")
        self.submodule("uart", target)
