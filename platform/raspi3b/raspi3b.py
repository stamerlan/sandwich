import atexit
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

firmware = None
toolchain: fwbuild.toolchains.gcc = \
    fwbuild.toolchains.gcc.find("aarch64-none-elf-")
_config_main = sys.modules["__main__"].__file__

class platform(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app):
        super().__init__(name="platform", target=target)
        self.src("startup.S", "init.cc")
        self.src("retarget.cc", variables={"cxxflags": "$cxxflags -fno-lto"})

        # Add necessary flags to target
        target.gen_binary = True
        target.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"
        target.ldflags += "-nostartfiles", "-specs=nosys.specs"
        target.ldflags += "-flto"
        if target.toolchain.ld.version >= (2, 39):
            target.ldflags += "-Wl,--no-warn-rwx-segment"
        target.ldscript = "$topdir/platform/raspi3b/raspi3b.ld"
        target.ldlibs += "-lgcc"

def cxx_target(name: str):
    global firmware
    if firmware is not None:
        raise RuntimeError("raspi3b target supports one target only")

    srcdir = fwbuild.utils.get_caller_filename().parent
    firmware = fwbuild.targets.cxx_app("kernel8", toolchain, srcdir)
    firmware.submodule(platform)

    return firmware

@atexit.register
def write_build_files():
    global firmware

    config_h = fwbuild.write_autoconf(fwbuild.topout / "config.h")
    config   = fwbuild.write_conf(fwbuild.topout / ".config")

    with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja") as writer:
        if config_h is not None:
            firmware.cxxflags += "-I." # Output directory

        writer.variable("topdir", fwbuild.topdir.as_posix())
        writer.newline()

        toolchain.write_ninja_file(writer, firmware)
        writer.newline()

        configure_cmd = fwbuild.utils.shell_cmd()
        if config is not None:
            configure_cmd.cmd(sys.executable, [_config_main, "-c", ".config"])
        else:
            configure_cmd.cd(pathlib.Path.cwd())
            configure_cmd.cmd(sys.executable, sys.argv)

        writer.comment("Regenerate build file if build script changed")
        writer.rule("configure", command=configure_cmd, generator=True,
                    description="CONFIGURE")
        writer.build("build.ninja", "configure",
            implicit=sorted(fwbuild.conf_files))
