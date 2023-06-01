import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

class Raspi3bPlatform(fwbuild.platforms.base):
    name: str = "raspi3b"
    firmware: fwbuild.targets.cxx_app | None = None
    toolchain: fwbuild.toolchains.gcc | None = None

    class cxx_module(fwbuild.targets.cxx_module):
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
            target.ldscript = pathlib.Path(__file__).parent / "raspi3b.ld"
            target.ldlibs += "-lgcc"

    def __init__(self):
        if Raspi3bPlatform.toolchain is None:
            Raspi3bPlatform.toolchain = fwbuild.toolchains.gcc.find("aarch64-none-elf-")

    def cxx_target(self, name: str):
        if Raspi3bPlatform.firmware is not None:
            raise RuntimeError("raspi3b platform supports one target only")

        srcdir = fwbuild.utils.get_caller_filename().parent
        Raspi3bPlatform.firmware = fwbuild.targets.cxx_app("kernel8", Raspi3bPlatform.toolchain, srcdir)
        Raspi3bPlatform.firmware.submodule(Raspi3bPlatform.cxx_module)

        return Raspi3bPlatform.firmware

    def write_buildfiles(self, entry_point_filename: str):
        config_h = fwbuild.write_autoconf(fwbuild.topout / "config.h")
        config   = fwbuild.write_conf(fwbuild.topout / ".config")

        with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja") as writer:
            if config_h is not None:
                Raspi3bPlatform.firmware.cxxflags += "-I." # Output directory

            writer.variable("topdir", fwbuild.topdir.as_posix())
            writer.newline()

            Raspi3bPlatform.toolchain.write_build_file(writer, Raspi3bPlatform.firmware)
            writer.newline()

            configure_cmd = fwbuild.utils.shell_cmd()
            if config is not None:
                configure_cmd.cmd(sys.executable, [entry_point_filename, "-c", ".config"])
            else:
                configure_cmd.cd(pathlib.Path.cwd())
                configure_cmd.cmd(sys.executable, sys.argv)

            writer.comment("Regenerate build file if build script changed")
            writer.rule("configure", command=configure_cmd, generator=True,
                        description="CONFIGURE")
            writer.build("build.ninja", "configure",
                implicit=sorted(fwbuild.conf_files))
