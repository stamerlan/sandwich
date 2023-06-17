from fwbuild.ninja_syntax import Writer
from itertools import chain
from pathlib import Path
import contextlib
import fwbuild

class build_artifacts(object):
    def __init__(self):
        objs: list[Path] = []

def _build_compile(w: Writer, module: fwbuild.cxx_module, outdir: Path,
                   reset_flags: bool = False) -> list[Path]:
    w.comment(f"Module: {module}")
    w.variable("srcdir", module.srcdir)
    w.variable("outdir", outdir.as_posix())

    flags = {
        "asflags" : str(module.asflags),
        "cxxflags": " ".join(chain(module.cxxflags,
                                   ['-I' + str(i) for i in module.includes]))
    }
    for name, value in flags.items():
        if reset_flags:
            w.variable(name, value)
        elif value:
            w.variable(name, f"${name} {value}")
    w.newline()

    objs = []
    for src in module.sources:
        obj_fname = Path("$outdir", src.path.stem).with_suffix(".o")
        print(f"{src}->{obj_fname.as_posix()}{f' {src.vars}' if src.vars else ''}")

        if src.path.suffix in (".cc", ".cxx", ".cpp"):
            w.build(obj_fname.as_posix(), "cxx", str(src), **src.vars)
        elif src.path.suffix in (".S"):
            w.build(obj_fname.as_posix(), "as", str(src), **src.vars)
        else:
            raise RuntimeError(f"{module.name}@{module.srcdir}: Unsupported source file suffix '{src}'")

        objs.append(Path(outdir, *obj_fname.parts[1:]))

    for mod in module.submodules:
        buildfile = outdir / mod.name / f"{mod.name}-build.ninja"
        w.subninja(buildfile.as_posix())

        with open(buildfile, "w") as f:
            objs.extend(compile(Writer(f), mod, buildfile.parent))

    return objs


class gcc(fwbuild.toolchain):
    @staticmethod
    def find(prefix: str = "", *search_dirs) -> "gcc":
        for cc in fwbuild.tool.find_all(prefix + "gcc", search_dirs):
            with contextlib.suppress(FileNotFoundError):
                return gcc(prefix, cc.path.parent)
        raise FileNotFoundError(f'Toolchain "{prefix}gcc" not found')

    def __init__(self, prefix: str, dir: Path):
        super().__init__(prefix + "gcc")
        self._prefix = prefix

        self.tools.cc      = fwbuild.tool(dir, prefix + "gcc",     name="cc")
        self.tools.ar      = fwbuild.tool(dir, prefix + "ar",      name="ar")
        self.tools.cxx     = fwbuild.tool(dir, prefix + "g++",     name="cxx")
        self.tools.ld      = fwbuild.tool(dir, prefix + "ld",      name="ld")
        self.tools.objcopy = fwbuild.tool(dir, prefix + "objcopy", name="objcopy")
        self.tools.objdump = fwbuild.tool(dir, prefix + "objdump", name="objdump")

    def build_cxx_app(self, target: fwbuild.cxx_app, outdir: Path, w: Writer):
        w.comment(f'Build target "{target.name}" using {self}')
        w.newline()

        w.variable("ar", self.tools.ar)
        w.variable("as", self.tools.cc)
        w.variable("cc", self.tools.cc)
        w.variable("cxx", self.tools.cxx)
        w.variable("objcopy", self.tools.objcopy)
        w.variable("objdump", self.tools.objdump)
        w.newline()

        w.comment(f'Rules for target "{target.name}"')
        w.rule("as",
            command="$as -MMD -MT $out -MF $out.d $asflags -c $in -o $out",
            depfile="$out.d",
            deps="gcc",
            description="AS $out")
        w.rule("cxx",
            command="$cxx -MMD -MT $out -MF $out.d $cxxflags -c $in -o $out",
            depfile="$out.d",
            deps="gcc",
            description="CXX $out")
        w.rule("objcopy",
            command="$objcopy --output-target binary $in $out",
            description="OBJCOPY $out")
        w.rule("objdump",
            command=fwbuild.shellcmd("$objdump", "--source",
                "--disassemble-all", "--demangle", "--include=$topdir", "$in",
                stdout="$out"),
            description="OBJDUMP $out")
        w.rule("ld",
            command="$cxx $ldflags -o $out $in $ldlibs",
            description="LD $out")
        w.newline()

        # Compile
        artifacts = build_artifacts()
        artifacts.objs = _build_compile(w, target, outdir, True)
        print(artifacts.objs)

        return True
