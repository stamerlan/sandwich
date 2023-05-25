import atexit
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

firmware = None
toolchain: fwbuild.toolchains.gcc = \
    fwbuild.toolchains.gcc.find("aarch64-none-elf-")

class platform_module(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app,
                 toolchain : fwbuild.toolchains.gcc):
        super().__init__()
        self.src("startup.S", "init.cc")
        self.src("retarget.cc", variables={"cxxflags": "$cxxflags -fno-lto"})

        # Add necessary flags to target
        target.gen_binary = True
        target.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"
        target.ldflags += "-nostartfiles", "-specs=nosys.specs"
        target.ldflags += "-flto"
        if toolchain.ld.version >= (2, 39):
            target.ldflags += "-Wl,--no-warn-rwx-segment"
        target.ldscript = "$topdir/platform/raspi3b/raspi3b.ld"
        target.ldlibs += "-lgcc"

def cxx_target(name: str):
    global firmware
    if firmware is not None:
        raise RuntimeError("raspi3b target supports one target only")

    srcdir = fwbuild.utils.get_caller_filename().parent
    if srcdir.is_relative_to(fwbuild.topdir):
        srcdir = pathlib.Path("$topdir", srcdir.relative_to(fwbuild.topdir))

    firmware = fwbuild.targets.cxx_app("kernel8", srcdir)
    firmware.submodule(platform_module(firmware, toolchain))

    return firmware

@atexit.register
def write_build_files():
    global firmware

    config_h = fwbuild.write_autoconf(fwbuild.topout / "config.h")
    with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja", config_h) as writer:
        if config_h is not None:
            firmware.cxxflags += "-I." # Output directory

        writer.variable("topdir", fwbuild.topdir.as_posix())
        toolchain.write_ninja_file(writer, firmware)
