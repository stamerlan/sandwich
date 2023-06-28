import fwbuild

@fwbuild.target
class bcm2837_mbox(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        if target.conf.BCM2837_MBOX:
            self.src("src/bcm2837_mbox.cc")

        target.include("include")
