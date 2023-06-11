import fwbuild
import fwbuild.targets
import pathlib

class mbox(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app):
        super().__init__("mbox", target)
        if fwbuild.conf.HOST_UART:
            self.src("src/mbox.cc")

        target.include(fwbuild.this_dir / "include")
