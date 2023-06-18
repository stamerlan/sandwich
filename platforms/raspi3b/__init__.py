from pathlib import Path
import fwbuild

@fwbuild.build
class raspi3b_platform(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target, name="platform")

        self.src("startup.S", "init.cc")
        self.src("retarget.cc", variables={"cxxflags": "$cxxflags -fno-lto"})

        # Add platform-specific flags to target
        target.binary = True

        target.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"
        target.cxxflags += "-ffreestanding"

        target.ldflags += "-nostartfiles", "-specs=nosys.specs"
        target.ldflags += "-flto"
        if target.toolchain.tools.ld.version >= (2, 39):
            target.ldflags += "-Wl,--no-warn-rwx-segment"
        target.ldscript = "raspi3b.ld"


class raspi3b(fwbuild.platform_base):
    def __init__(self, conf: fwbuild.kconfig):
        super().__init__(conf)

        self.targets: list[fwbuild.cxx_module] = []

        self.toolchain:      fwbuild.toolchain = None
        self.host_toolchain: fwbuild.toolchain = None

        for cls in fwbuild.build_cls:
            if issubclass(cls, fwbuild.cxx_gtest):
                if self.host_toolchain is None:
                    self.host_toolchain = fwbuild.toolchains.gcc.find()
                self.targets.append(cls(conf, self.host_toolchain))
            elif issubclass(cls, fwbuild.cxx_app):
                if self.toolchain is None:
                    self.toolchain = fwbuild.toolchains.gcc.find("aarch64-none-elf-")
                app = cls(conf, self.toolchain)
                app.submodule("raspi3b_platform")
                self.targets.append(app)
            elif issubclass(cls, fwbuild.cxx_module):
                pass
            else:
                raise RuntimeError(f"Unexpected target {cls}")

    def build_cxx_app(self, topout: Path, target: fwbuild.cxx_app,
                      w: fwbuild.ninja_writer):
        return target.toolchain.build_cxx_app(topout, target, w)
