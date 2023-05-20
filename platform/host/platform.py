import atexit
import fwbuild
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import shlex
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
    interpreter_path = pathlib.Path(sys.executable).as_posix()
    cmdline = ' '.join(map(shlex.quote, sys.argv[1:]))

    for name, target in targets.items():
        if len(targets) > 1:
            build_filename = name + "-build.ninja"
            outdir = name
        else:
            build_filename = "build.ninja"
            outdir = "."

        with fwbuild.utils.ninja_writer(fwbuild.outdir / build_filename) as writer:
            toolchain.write_ninja_file(writer, target, outdir=outdir)

    if len(targets) > 1:
        with fwbuild.utils.ninja_writer(fwbuild.outdir / "build.ninja") as n:
            n.variable("srcdir", fwbuild.srcdir.as_posix())
            n.newline()

            for name, target in targets.items():
                n.subninja(name + "-build.ninja")
