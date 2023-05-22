import atexit
import fwbuild
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

targets: dict[str, fwbuild.targets.cxx_app] = {}
toolchain = fwbuild.toolchains.gcc.find()
_configure_path = pathlib.Path(sys.modules["__main__"].__file__).as_posix()

def cxx_target(name: str):
    global targets

    if name in targets:
        raise RuntimeError(f'Target "{name}" already defined')

    srcdir = fwbuild.utils.get_caller_filename().parent
    app = fwbuild.targets.cxx_app(name, srcdir=srcdir)
    targets[name] = app

    return app

@atexit.register
def write_build_files():
    with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja") as writer:
        writer.variable("topdir", fwbuild.topdir.as_posix())
        writer.variable("topout", ".")
        writer.newline()

        for name, target in targets.items():
            if len(targets) == 1:
                toolchain.write_ninja_file(writer, target)
            else:
                build_filename = pathlib.Path(name, f"{name}-build.ninja")
                writer.subninja(f"$topout/{build_filename.as_posix()}")
                with fwbuild.utils.ninja_writer(fwbuild.topout / build_filename) as target_writer:
                    toolchain.write_ninja_file(target_writer, target, build_filename.parent)
