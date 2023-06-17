import fwbuild

@fwbuild.build
class mbox(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        if target.conf.HOST_UART:
            self.src("src/mbox.cc")

        target.include("include")
