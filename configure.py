#!/usr/bin/env python3
import argparse
import scripts.fwbuild as fwbuild

parser = argparse.ArgumentParser("Sandwich configuration script")
parser.add_argument("--platform", choices=["raspi3b", "host"],
                    default="raspi3b", help="Target platform")
conf = parser.parse_args()

fwbuild.platform.load(fwbuild.srcdir / f"platform/{conf.platform}/platform.py")
if str(fwbuild.outdir) != ".":
    fwbuild.outdir /= conf.platform

fw = fwbuild.platform.cxx_target("fw")
fw.cxxflags += "-std=c++23", "-g", "-O3"
fw.cxxflags += "-fcheck-new", "-flto", "-fno-rtti", "-fno-exceptions"
fw.cxxflags += "-fno-threadsafe-statics"
fw.cxxflags += "-Wall", "-Wextra", "-Werror", "-Weffc++",
fw.cxxflags += "-Wmultiple-inheritance", "-Wvirtual-inheritance"
fw.cxxflags += "-ffile-prefix-map=$srcdir/="

fw.src("src/main.cc")
