import fwbuild

@fwbuild.target
class arch_host(fwbuild.cxx_module):
    """ A platform for unit testing and host implementation """
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        self.src("src/irq.cc")
