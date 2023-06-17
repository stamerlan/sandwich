from fwbuild.ninja_syntax import Writer
from itertools import chain
from pathlib import Path
import contextlib
import fwbuild
import sys

class build_artifacts(object):
    def __init__(self):
        self.app : Path | None = None
        self.objs: list[Path]  = []
        self.bin : Path | None = None
        self.dasm: Path | None = None
        self.map : Path | None = None

        # Default build files
        self.defaults: list[str] = []

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

        # Link
        artifacts.app = outdir / target.name
        if self._prefix:
            artifacts.app = artifacts.app.with_suffix(".elf")
        elif sys.platform == "win32":
            artifacts.app = artifacts.app.with_suffix(".exe")

        w.comment(f"Link {artifacts.app.as_posix()}")
        w.variable("ldflags", target.ldflags)
        w.variable("ldlibs", " ".join(["-l" + lib for lib in target.ldlibs]))
        w.newline()

        ld_vars = {
            "implicit": [],
            "implicit_outputs": [],
            "variables": {
                "ldflags": []
            }
        }

        if target.ldscript:
            ld_vars["implicit"].append(str(target.ldscript))
            ld_vars["variables"]["ldflags"].append(f"-T {target.ldscript}")
        if target.mapfile:
            artifacts.map = artifacts.app.with_suffix(".map")
            ld_vars["implicit"].append(artifacts.map.as_posix())
            ld_vars["variables"]["ldflags"].append(
                f"-Xlinker -Map={artifacts.map.as_posix()}")

        ld_vars["variables"] = {k: v for k, v in ld_vars["variables"].items() if v}
        for name, value in ld_vars["variables"].items():
            ld_vars["variables"][name] = \
                ' '.join(ld_vars["variables"][name]) + f" ${name}"

        artifacts.defaults.append(artifacts.app.as_posix())
        w.build(artifacts.app.as_posix(), "ld",
            [p.as_posix() for p in artifacts.objs],
            **ld_vars)

        # Binary
        if target.binary:
            artifacts.bin = artifacts.app.with_suffix(".bin")
            w.build(artifacts.bin.as_posix(), "objcopy",
                    artifacts.app.as_posix())
            artifacts.defaults.append(artifacts.bin.as_posix())

        # Disassemble
        if target.disassembly:
            artifacts.dasm = artifacts.app.with_suffix(".asm")
            w.build(artifacts.dasm.as_posix(), "objdump",
                    artifacts.app.as_posix())
            artifacts.defaults.append(artifacts.dasm.as_posix())

        w.newline()

        # Add files to be build by default
        if target.default:
            w.default(artifacts.defaults)

        return artifacts
