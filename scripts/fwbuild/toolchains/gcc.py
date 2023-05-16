import fwbuild.targets.cxx
import fwbuild.utils
import os
import pathlib
import subprocess
import sys
import typing

def to_shell(cmdline: str):
    if sys.platform == "win32":
        return f'cmd /c "{cmdline}"'
    else:
        return cmdline
class program_ld(fwbuild.utils.program):
    @property
    def version(self):
        if not hasattr(self, "_version"):
            version_str = subprocess.check_output([str(self), "-v"]).decode()
            version_str = version_str.split()[-1]
            self._version = tuple([int(i) for i in version_str.split('.')])
        return self._version


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
    def find(prefix="", dirs=[]) -> typing.Self:
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

    @property
    def ld(self):
        return self._ld

    def __str__(self) -> str:
        return f"{self._prefix + 'gcc'} at {self._cc}"

    def write_ninja_file(self, output,
            target: fwbuild.targets.cxx,
            outdir: str | pathlib.Path = "."):
        n = fwbuild.utils.ninja_syntax.Writer(output)

        n.comment(f"Build {target.name} using {self._cc}")
        n.newline()

        n.variable("srcdir", target.srcdir)
        if isinstance(outdir, pathlib.Path):
            outdir = outdir.as_posix()
        n.variable("outdir", outdir)
        n.newline()

        n.variable("ar", self._ar)
        n.variable("as", self._cc)
        n.variable("cc", self._cc)
        n.variable("cxx", self._cxx)
        n.variable("objcopy", self._objcopy)
        n.variable("objdump", self._objdump)
        n.newline()

        n.variable("asflags", target.asflags)
        n.variable("cxxflags", target.cxxflags)
        n.variable("ldflags", target.ldflags)
        n.variable("ldlibs", target.ldlibs)
        n.newline()

        n.rule("as",
            command="$as -MMD -MT $out -MF $out.d $asflags -c $in -o $out",
            depfile="$out.d",
            deps="gcc",
            description="AS $out")
        n.newline()

        n.rule("cxx",
            command="$cxx -MMD -MT $out -MF $out.d $cxxflags -c $in -o $out",
            depfile="$out.d",
            deps="gcc",
            description="CXX $out")
        n.newline()

        n.rule("objcopy",
            command="$objcopy --output-target binary $in $out",
            description="OBJCOPY $out")
        n.newline()

        n.rule("objdump",
            command=to_shell("$objdump --source --disassemble-all --demangle --include=$srcdir $in > $out"),
            description="OBJDUMP $out")
        n.newline()

        n.rule("ld",
            command="$cxx $ldflags -o $out $in $ldlibs",
            description="LD $out")
        n.newline()

        # Compile
        objs = []
        for src in target.sources:
            if src.path.is_absolute():
                obj_filename = src.filename.with_suffix(".o").name
            elif src.path.parts[0] in ("$outdir", "$srcdir"):
                obj_filename = pathlib.Path("$outdir", *src.path.parts[1:])
                obj_filename = obj_filename.with_suffix(".o").as_posix()
            else:
                raise RuntimeError(f"{target.name}: Unexpected source file path '{src}'")

            if src.path.suffix in (".cc", ".cxx", ".cpp"):
                objs += n.build(obj_filename, "cxx", str(src), **src.vars)
            elif src.path.suffix in (".S"):
                objs += n.build(obj_filename, "as", str(src), **src.vars)
            else:
                raise RuntimeError(f"{target.name}: Unsupported source file suffix '{src}'")
        n.newline()

        # Link
        outfile_name = f"$outdir/{target.name}"
        if self._prefix:
            outfile_name += ".elf"
        elif sys.platform == "win32":
            outfile_name += ".exe"

        implicit_outputs = []
        add_ldflags = []
        implicit_deps = []
        if target.ldscript:
            add_ldflags.append(f"-T {target.ldscript}")
            implicit_deps.append(str(target.ldscript))
        if target.gen_map:
            mapfile_name = f"$outdir/{target.name}.map"
            implicit_outputs.append(mapfile_name)
            add_ldflags.append(f"-Xlinker -Map={mapfile_name}")

        ld_rule_vars = {}
        if add_ldflags:
            ld_rule_vars["ldflags"] = ' '.join(f for f in add_ldflags) + " $ldflags"

        n.build(outfile_name, "ld", objs,
            implicit=implicit_deps, implicit_outputs=implicit_outputs,
            variables=ld_rule_vars)

        # Binary
        if target.gen_binary:
            binfile_name = f"$outdir/{target.name}.bin"
            n.build(binfile_name, "objcopy", outfile_name)

        # Disassemble
        if target.gen_dasm:
            dasmfile_name = f"$outdir/{target.name}.asm"
            n.build(dasmfile_name, "objdump", outfile_name)
