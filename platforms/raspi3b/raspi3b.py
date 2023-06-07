import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib

fwbuild.deps.add(__file__)

class Raspi3bPlatform(fwbuild.platforms.base):
    name: str = "raspi3b"
    toolchain: fwbuild.toolchains.gcc | None = None

    class platform_module(fwbuild.targets.cxx_module):
        def __init__(self, target: fwbuild.targets.cxx_app):
            super().__init__(name="platform", target=target)
            self.src("startup.S", "init.cc")
            self.src("retarget.cc", variables={"cxxflags": "$cxxflags -fno-lto"})

            # Add platform-specific flags to target
            target.gen_binary = True
            target.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"
            target.ldflags += "-nostartfiles", "-specs=nosys.specs"
            target.ldflags += "-flto"
            if target.toolchain.ld.version >= (2, 39):
                target.ldflags += "-Wl,--no-warn-rwx-segment"
            target.ldscript = pathlib.Path(self.srcdir, "raspi3b.ld")
            target.ldlibs += "gcc"

    def __init__(self):
        super().__init__()
        if Raspi3bPlatform.toolchain is None:
            Raspi3bPlatform.toolchain = fwbuild.toolchains.gcc.find("aarch64-none-elf-")

    def cxx_app(self, name: str):
        if len(Raspi3bPlatform.targets) == 1:
            raise RuntimeError("raspi3b platform supports one target only")

        srcdir = fwbuild.utils.caller().dir
        app = super().cxx_app("kernel8", Raspi3bPlatform.toolchain, srcdir)
        app.submodule(Raspi3bPlatform.platform_module)
        return app
