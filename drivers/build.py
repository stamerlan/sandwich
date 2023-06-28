import fwbuild
import drivers.bcm2837_mbox.build
import drivers.uart.build

@fwbuild.target
class drivers(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        self.submodule("bcm2837_mbox")
        self.submodule("uart")
