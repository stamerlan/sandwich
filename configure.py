#!/usr/bin/env python3
import os
import pathlib
import scripts.fwbuild as fwbuild
import sys

target_platform = "raspi3"
#target_platform = "win"

hello = fwbuild.cxx_target("hello")
hello.cxxflags += "-std=c++23", "-g", "-O3"
hello.cxxflags += "-fcheck-new", "-flto", "-fno-rtti", "-fno-exceptions"
hello.cxxflags += "-fno-threadsafe-statics"
hello.cxxflags += "-Wall", "-Wextra", "-Werror", "-Weffc++",
hello.cxxflags += "-Wmultiple-inheritance", "-Wvirtual-inheritance"
hello.cxxflags += "-ffile-prefix-map=$srcdir/="

hello.src("src/main.cc")

if target_platform == "win":
    gcc = fwbuild.gcc.find()
elif target_platform == "raspi3":
    gcc = fwbuild.gcc.find("aarch64-none-elf-")

    hello.gen_binary = True
    hello.gen_dasm = True
    hello.gen_map = True

    hello.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"

    hello.ldflags += "-nostartfiles", "-specs=nosys.specs"
    hello.ldflags += "-flto"

    print(f"Binutils v{'.'.join(str(v) for v in gcc.ld.version)}")
    if gcc.ld.version >= (2, 39):
        hello.ldflags += "-Wl,--no-warn-rwx-segment"

    hello.ldscript = "src/raspi3b.ld"

    hello.ldlibs += "-lgcc"

    hello.src("src/raspi3_startup.S")
    hello.src("src/raspi3_init.cc")
    hello.src("src/retarget.cc", variables={"cxxflags": "$cxxflags -fno-lto"})
else:
    print(f"Unknown platform '{target_platform}'", file=sys.stderr)
    sys.exit(1)

srcdir = pathlib.Path(__file__).parent
if os.path.samefile(srcdir, os.getcwd()):
    outdir = pathlib.Path("bin/")
else:
    outdir = pathlib.Path(".")
outdir.mkdir(parents=True, exist_ok=True)

with open(outdir / "build.ninja", "w") as buildfile:
    gcc.write_ninja_file(buildfile, hello)
    n = fwbuild.NinjaWriter(buildfile)
    n.newline()
    n.comment("Regenerate build file if build script changed.")
    n.rule("configure",
        command=f"{pathlib.Path(sys.executable).as_posix()} {pathlib.Path(__file__).as_posix()}",
        generator=True,
        description="CONFIGURE")
    # TODO: Add dependency from fwbuild content
    n.build("$outdir/build.ninja", "configure",
            implicit=["$srcdir/configure.py"])
