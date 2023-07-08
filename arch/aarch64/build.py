import fwbuild

@fwbuild.target
class arch_aarch64(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        target.include("include")

        self.src("src/irq.cc")
