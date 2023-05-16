import atexit
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import shlex
import sys

_kernel8_target = None
_toolchain = fwbuild.toolchains.gcc.find("aarch64-none-elf-")
_configure_path = pathlib.Path(sys.modules["__main__"].__file__).as_posix()

def cxx_target(name: str):
    global _kernel8_target
    if _kernel8_target is not None:
        raise RuntimeError("raspi3b target supports one target only")

    srcdir = fwbuild.utils.get_caller_filename().parent
    platform_dir = pathlib.Path(__file__).parent
    if platform_dir.is_relative_to(srcdir):
        platform_dir = pathlib.Path("$srcdir", platform_dir.relative_to(srcdir))

    _kernel8_target = fwbuild.targets.cxx("kernel8", srcdir=srcdir)
    _kernel8_target.gen_binary = True
    _kernel8_target.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"
    _kernel8_target.ldflags += "-nostartfiles", "-specs=nosys.specs"
    _kernel8_target.ldflags += "-flto"
    if _toolchain.ld.version >= (2, 39):
        _kernel8_target.ldflags += "-Wl,--no-warn-rwx-segment"
    _kernel8_target.ldscript = platform_dir / "raspi3b.ld"
    _kernel8_target.ldlibs += "-lgcc"

    _kernel8_target.src([platform_dir / "startup.S", platform_dir / "init.cc"])
    _kernel8_target.src(platform_dir / "retarget.cc",
        variables={"cxxflags": "$cxxflags -fno-lto"})

    return _kernel8_target

@atexit.register
def write_build_files():
    interpreter_path = pathlib.Path(sys.executable).as_posix()
    cmdline = ' '.join(map(shlex.quote, sys.argv[1:]))

    fwbuild.outdir.mkdir(parents=True, exist_ok=True)
    with open(fwbuild.outdir / "build.ninja", "w") as build_file:
        fwbuild.platform._toolchain.write_ninja_file(build_file, _kernel8_target)
        n = fwbuild.utils.ninja_syntax.Writer(build_file)
        n.newline()

        n.comment("Regenerate build file if build script changed.")
        n.rule("configure",
            command=f"{interpreter_path} {_configure_path} {cmdline}",
            generator=True,
            description="CONFIGURE")
        n.build("$outdir/build.ninja", "configure", implicit=_kernel8_target.build_files)