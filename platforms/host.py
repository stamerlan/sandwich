import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

class HostPlatform(fwbuild.platforms.base):
    name: str = "host"
    targets: dict[str, fwbuild.targets.cxx_app] = {}
    toolchain: fwbuild.toolchains.gcc | None = None

    def __init__(self):
        if HostPlatform.toolchain is None:
            HostPlatform.toolchain = fwbuild.toolchains.gcc.find()

    def cxx_target(self, name: str):
        if name in HostPlatform.targets:
            raise RuntimeError(f'Target "{name}" already defined')

        srcdir = fwbuild.utils.get_caller_filename().parent
        app = fwbuild.targets.cxx_app(name, HostPlatform.toolchain, srcdir=srcdir)
        HostPlatform.targets[name] = app

        return app

    def write_buildfiles(self, entry_point_filename: str):
        config_h = fwbuild.conf.write_autoconf(fwbuild.topout / "config.h")
        config   = fwbuild.conf.write_conf(fwbuild.topout / ".config")

        with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja") as writer:
            writer.variable("topdir", fwbuild.topdir.as_posix())
            writer.newline()

            for name, target in HostPlatform.targets.items():
                if config_h is not None:
                    target.cxxflags += "-I." # Output directory

                if len(HostPlatform.targets) == 1:
                    HostPlatform.toolchain.write_build_file(writer, target)
                else:
                    build_filename = pathlib.Path(name, f"{name}-build.ninja")
                    writer.subninja(f"${build_filename.as_posix()}")
                    with fwbuild.utils.ninja_writer(fwbuild.topout / build_filename) as target_writer:
                        HostPlatform.toolchain.write_build_file(target_writer, target, build_filename.parent)
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
                implicit=[p.as_posix() for p in sorted(fwbuild.conf_files | fwbuild.conf.files)])
