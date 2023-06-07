from typing import Optional
import itertools
import fwbuild
import fwbuild.targets.cxx_app
import fwbuild.utils
import os
import pathlib
import subprocess
import sys

fwbuild.deps.add(__file__)

class build_artifacts(object):
    def __init__(self):
        self.exe : Optional[pathlib.Path] = None
        self.objs: list[pathlib.Path] = []
        self.bin : Optional[pathlib.Path] | None = None
        self.dasm: Optional[pathlib.Path] = None
        self.map : Optional[pathlib.Path] = None

class program_ld(fwbuild.utils.program):
    @property
    def version(self):
        if not hasattr(self, "_version"):
            version_str = subprocess.check_output([str(self), "-v"]).decode()
            version_str = version_str.split()[-1]
            self._version = tuple([int(i) for i in version_str.split('.')])
        return self._version


def compile(writer: fwbuild.utils.ninja_syntax.Writer,
            module: fwbuild.targets.cxx_module,
            outdir: pathlib.Path = pathlib.Path(),
            reset_flags: bool = True) -> list[pathlib.Path]:
    writer.comment(f"Module: {module.name}")
    writer.variable("srcdir", module.srcdir)
    writer.variable("outdir", outdir.as_posix())

    flags = {
        "asflags" : str(module.asflags),
        "cxxflags": " ".join(itertools.chain(
                            module.cxxflags,
                            ['-I' + str(i) for i in module.includes]
                    ))
    }

    for name, value in flags.items():
        if reset_flags:
            writer.variable(name, value)
        elif value:
            writer.variable(name, f"${name} {value}")
    writer.newline()

    objs = []
    for src in module.sources:
        obj_fname = pathlib.Path("$outdir", src.path.stem).with_suffix(".o")

        if src.path.suffix in (".cc", ".cxx", ".cpp"):
            writer.build(obj_fname.as_posix(), "cxx", str(src), **src.vars)
        elif src.path.suffix in (".S"):
            writer.build(obj_fname.as_posix(), "as", str(src), **src.vars)
        else:
            raise RuntimeError(f"{module.name}@{module.srcdir}: Unsupported source file suffix '{src}'")

        objs.append(pathlib.Path(outdir, *obj_fname.parts[1:]))

    for mod in module.submodules:
        buildfile = outdir / mod.name / f"{mod.name}-build.ninja"
        writer.subninja(buildfile.as_posix())
        with fwbuild.utils.ninja_writer(fwbuild.topout / buildfile) as w:
            objs.extend(compile(w, mod, buildfile.parent, False))

    return objs

class gcc(object):
    @staticmethod
    def list(prefix="", dirs=[]):
        if isinstance(dirs, str) or isinstance(dirs, pathlib.Path):
            dirs = [dirs]
        path = os.environ.get("PATH", None)
        if path is None:
            try:
                path = os.confstr("CS_PATH")
            except (AttributeError, ValueError):
                # os.confstr() or CS_PATH is not available
                path = os.defpath
        if path is not None:
            path = path.split(os.pathsep)
        else:
            path = []
        path.extend(dirs)

        for d in path:
            try:
                yield gcc(d, prefix)
            except FileNotFoundError:
                pass

    @staticmethod
    def find(prefix="", dirs=[]) -> 'gcc':
        try:
            return next(gcc.list(prefix, dirs))
        except StopIteration:
            raise FileExistsError(f'Toolchain "{prefix}gcc" not found') from None

    def __init__(self, directory, prefix=""):
        self._ar  = fwbuild.utils.program(directory, prefix + "ar")
        self._cc  = fwbuild.utils.program(directory, prefix + "gcc")
        self._cxx = fwbuild.utils.program(directory, prefix + "g++")
        self._ld  = program_ld(directory, prefix + "ld")
        self._objcopy = fwbuild.utils.program(directory, prefix + "objcopy")
        self._objdump = fwbuild.utils.program(directory, prefix + "objdump")
        self._prefix = prefix

    def __str__(self) -> str:
        return f"{self._prefix + 'gcc'}@{self._cc.path.parent.as_posix()}"

    @property
    def ld(self) -> fwbuild.utils.program:
        return self._ld

    def write_buildfile(self, writer: fwbuild.utils.ninja_syntax.Writer,
            target: fwbuild.targets.cxx_app,
            outdir: str | pathlib.Path = pathlib.Path()) -> build_artifacts:
        outdir = pathlib.Path(outdir)
        artifacts = build_artifacts()

        writer.comment(f"Build {target.name} using {self}")
        writer.variable("ar", self._ar)
        writer.variable("as", self._cc)
        writer.variable("cc", self._cc)
        writer.variable("cxx", self._cxx)
        writer.variable("objcopy", self._objcopy)
        writer.variable("objdump", self._objdump)
        writer.newline()

        writer.comment("Rules")
        writer.rule("as",
            command="$as -MMD -MT $out -MF $out.d $asflags -c $in -o $out",
            depfile="$out.d",
            deps="gcc",
            description="AS $out")
        writer.rule("cxx",
            command="$cxx -MMD -MT $out -MF $out.d $cxxflags -c $in -o $out",
            depfile="$out.d",
            deps="gcc",
            description="CXX $out")
        writer.rule("objcopy",
            command="$objcopy --output-target binary $in $out",
            description="OBJCOPY $out")
        writer.rule("objdump",
            command=fwbuild.utils.shell_cmd("$objdump",
                args=["--source", "--disassemble-all", "--demangle",
                      "--include=$topdir", "$in"], stdout="$out"),
            description="OBJDUMP $out")
        writer.rule("ld",
            command="$cxx $ldflags -o $out $in $ldlibs",
            description="LD $out")
        writer.newline()

        # Compile
        artifacts.objs = compile(writer, target, outdir)
        writer.newline()

        # Link
        artifacts.exe = outdir / target.name
        if self._prefix:
            artifacts.exe = artifacts.exe.with_suffix(".elf")
        elif sys.platform == "win32":
            artifacts.exe = artifacts.exe.with_suffix(".exe")

        writer.comment(f"Link {artifacts.exe.as_posix()}")
        writer.variable("ldflags", target.ldflags)
        writer.variable("ldlibs", " ".join(["-l" + lib for lib in target.ldlibs]))
        writer.newline()

        default_targets = [artifacts.exe.as_posix()]
        implicit_outputs = []
        add_ldflags = []
        implicit_deps = []
        if target.ldscript:
            add_ldflags.append(f"-T {target.ldscript}")
            implicit_deps.append(str(target.ldscript))
        if target.gen_map:
            artifacts.map = artifacts.exe.with_suffix(".map")
            implicit_outputs.append(artifacts.map.as_posix())
            add_ldflags.append(f"-Xlinker -Map={artifacts.map.as_posix()}")

        ld_rule_vars = {}
        if add_ldflags:
            ld_rule_vars["ldflags"] = ' '.join(f for f in add_ldflags) + " $ldflags"

        writer.build(artifacts.exe.as_posix(), "ld",
            [p.as_posix() for p in artifacts.objs],
            implicit=implicit_deps, implicit_outputs=implicit_outputs,
            variables=ld_rule_vars)

        # Binary
        if target.gen_binary:
            artifacts.bin = artifacts.exe.with_suffix(".bin")
            writer.build(artifacts.bin.as_posix(), "objcopy",
                         artifacts.exe.as_posix())
            default_targets.append(artifacts.bin.as_posix())

        # Disassemble
        if target.gen_dasm:
            artifacts.dasm = artifacts.exe.with_suffix(".asm")
            writer.build(artifacts.dasm.as_posix(), "objdump", artifacts.exe.as_posix())
            default_targets.append(artifacts.dasm.as_posix())

        writer.newline()

        if target.default_build:
            writer.default(default_targets)

        return artifacts
