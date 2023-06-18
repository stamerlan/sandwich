from pathlib import Path
import fwbuild

class platform_base(object):
    def __init__(self, conf: "fwbuild.kconfig"):
        fwbuild.deps.add(Path(__file__))
        fwbuild.deps.add(fwbuild.caller().filename)
        self.name = fwbuild.caller().cls.__name__

    def build_cxx_app(self, topout: Path, target: "fwbuild.cxx_app",
                      w: "fwbuild.ninja_writer"):
        raise NotImplementedError("fwbuild.platform_base.build_cxx_app()")
