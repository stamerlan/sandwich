import atexit
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

targets: dict[str, fwbuild.targets.cxx] = {}
toolchain = fwbuild.toolchains.gcc.find()
_configure_path = pathlib.Path(sys.modules["__main__"].__file__).as_posix()

def cxx_target(name: str):
    global targets

    if name in targets:
        raise RuntimeError(f'Target "{name}" already defined')

    srcdir = fwbuild.utils.get_caller_filename().parent
    app = fwbuild.targets.cxx(name, srcdir=srcdir)
    targets[name] = app

    return app

@atexit.register
def write_build_files():
    interpreter_path = pathlib.Path(sys.executable).as_posix()

    fwbuild.outdir.mkdir(parents=True, exist_ok=True)
    for name, target in targets.items():
        if len(targets) > 1:
            build_filename = name + "-build.ninja"
            outdir = name
        else:
            build_filename = "build.ninja"
            outdir = "."

        with open(fwbuild.outdir / build_filename, "w") as f:
            toolchain.write_ninja_file(f, target, outdir=outdir)

            n = fwbuild.utils.ninja_syntax.Writer(f)
            n.newline()

            n.comment("Regenerate build file if build script changed")
            n.rule("configure",
                command=f"{interpreter_path} {_configure_path}",
                generator=True,
                description="CONFIGURE")
            n.build(build_filename, "configure", implicit=target.build_files)

    if len(targets) > 1:
        with open(fwbuild.outdir / "build.ninja", "w") as build_file:
            n = fwbuild.utils.ninja_syntax.Writer(build_file)
            n.variable("srcdir", fwbuild.srcdir.as_posix())

            build_files = set()
            for name, target in targets.items():
                n.subninja(name + "-build.ninja")
                for f in target.build_files:
                    fpath = pathlib.Path(f.replace("$srcdir", target.srcdir))
                    try:
                        fpath = pathlib.Path("$srcdir", fpath.relative_to(fwbuild.srcdir))
                    except ValueError:
                        pass
                    build_files.add(fpath.as_posix())
            n.newline()

            n.comment("Regenerate build file if build script changed")
            n.rule("configure",
                command=f"{interpreter_path} {_configure_path}",
                generator=True,
                description="CONFIGURE")
            n.build("$outdir/" + build_filename, "configure",
                implicit=sorted(build_files))
