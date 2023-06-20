import fwbuild
import drivers.mbox.build
import drivers.uart.build

@fwbuild.target
class drivers(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        self.submodule("mbox")
        self.submodule("uart")
