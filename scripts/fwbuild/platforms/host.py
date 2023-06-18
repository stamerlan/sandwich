from pathlib import Path
import fwbuild
import fwbuild.toolchains

class host(fwbuild.platform_base):
    def __init__(self, conf: fwbuild.kconfig):
        super().__init__(conf)

        self.targets: list[fwbuild.cxx_module] = []
        self.toolchain = fwbuild.toolchains.gcc.find()

        for cls in fwbuild.build_cls:
            if issubclass(cls, fwbuild.cxx_app):
                self.targets.append(cls(conf, self.toolchain))
            elif issubclass(cls, fwbuild.cxx_module):
                pass
            else:
                raise RuntimeError(f"Unexpected target {cls}")

    def build_cxx_app(self, topout: Path, target: fwbuild.cxx_app,
                      w: fwbuild.ninja_writer) -> fwbuild.cxx_app.artifacts:
        return target.toolchain.build_cxx_app(topout, target, w)
