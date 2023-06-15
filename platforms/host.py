from fwbuild.ninja_syntax import Writer
from pathlib import Path
import fwbuild
import fwbuild.toolchains

class host(object):
    def __init__(self, conf: fwbuild.kconfig):
        fwbuild.deps.add(Path(__file__))

        self.targets: list[fwbuild.cxx_module] = []
        self.toolchain = fwbuild.toolchains.gcc.find()

        for cls in fwbuild.build_cls:
            if issubclass(cls, fwbuild.cxx_gtest):
                print(f"{cls.__name__}: GTest target is not supported")
            elif issubclass(cls, fwbuild.cxx_app):
                self.targets.append(cls(conf, self.toolchain))
            elif issubclass(cls, fwbuild.cxx_module):
                pass
            else:
                raise RuntimeError(f"Unexpected target {cls}")

    def build_cxx_app(self, target: fwbuild.cxx_app, outdir: Path, w: Writer):
        return self.toolchain.build_cxx_app(target, outdir, w)
