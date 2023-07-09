import fwbuild

@fwbuild.target
class display(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        target.include("include")

        if target.conf.PLATFORM_RASPI3B:
            self.src("src/raspi3b.cc")
        elif target.conf.PLATFORM_HOST:
            self.src("src/host.cc")
        else:
            raise NotImplementedError("Display doesn't support this platform")
