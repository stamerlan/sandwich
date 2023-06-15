from pathlib import Path
import fwbuild
import fwbuild.toolchains

class host(object):
    def __init__(self, conf: fwbuild.kconfig):
        fwbuild.deps.add(Path(__file__))

        self.targets = []
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
