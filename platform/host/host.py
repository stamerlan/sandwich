import atexit
import fwbuild
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

targets: dict[str, fwbuild.targets.cxx_app] = {}
toolchain = fwbuild.toolchains.gcc.find()
_config_main = sys.modules["__main__"].__file__

def cxx_target(name: str):
    global targets

    if name in targets:
        raise RuntimeError(f'Target "{name}" already defined')

    srcdir = fwbuild.utils.get_caller_filename().parent
    app = fwbuild.targets.cxx_app(name, toolchain, srcdir=srcdir)
    targets[name] = app

    return app

@atexit.register
def write_build_files():
    config_h = fwbuild.write_autoconf(fwbuild.topout / "config.h")
    config   = fwbuild.write_conf(fwbuild.topout / ".config")

    with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja") as writer:
        writer.variable("topdir", fwbuild.topdir.as_posix())
        writer.newline()

        for name, target in targets.items():
            if config_h is not None:
                target.cxxflags += "-I." # Output directory

            if len(targets) == 1:
                toolchain.write_build_file(writer, target)
            else:
                build_filename = pathlib.Path(name, f"{name}-build.ninja")
                writer.subninja(f"${build_filename.as_posix()}")
                with fwbuild.utils.ninja_writer(fwbuild.topout / build_filename) as target_writer:
                    toolchain.write_build_file(target_writer, target, build_filename.parent)
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
