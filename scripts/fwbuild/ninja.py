from pathlib import Path
import fwbuild
import fwbuild.ninja_syntax
import sys

def write_subninja(platform, target, filename: Path):
    if isinstance(target, fwbuild.cxx_gtest):
        return None
    elif isinstance(target, fwbuild.cxx_app):
        pass
    elif isinstance(target, fwbuild.cxx_module):
        return None
    else:
        raise RuntimeError(f'"{target}" has unexpected class {type(target)}')

    with open(filename, "w") as f:
        w = fwbuild.ninja_syntax.Writer(f)
        return platform.build_cxx_app(target, filename.parent, w)


def ninja(platform, buildfile_name: str | Path):
    buildfile_name = Path(buildfile_name)
    buildfile_name.parent.mkdir(parents=True, exist_ok=True)

    with open(buildfile_name, "w") as buildfile:
        w = fwbuild.ninja_syntax.Writer(buildfile)
        w.comment("DO NOT EDIT THIS FILE")
        w.comment("It is automatically generated by fwbuild using")
        w.comment(sys.modules["__main__"].__file__)
        w.newline()

        w.variable("topdir", fwbuild.topdir.as_posix())
        w.newline()

        for target in platform.targets:
            name = buildfile_name.parent / f"{target.name}-build.ninja"

            build = write_subninja(platform, target, name)
            if build is not None:
                w.subninja(name.as_posix())
