#!/usr/bin/env python3
import argparse
import scripts.fwbuild as fwbuild

parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("--platform", choices=["raspi3b", "host"],
                    default="host", help="Target platform")
conf = parser.parse_args()

fwbuild.platform.load(f"platform/{conf.platform}/platform.py")
if str(fwbuild.topout) != ".":
    fwbuild.topout /= conf.platform

app = fwbuild.platform.cxx_target("hello")
app.gen_dasm = True
app.gen_map = True

app.cxxflags += "-std=c++23", "-g", "-O3"
app.cxxflags += "-fcheck-new", "-flto", "-fno-rtti", "-fno-exceptions"
app.cxxflags += "-fno-threadsafe-statics"
app.cxxflags += "-Wall", "-Wextra", "-Werror", "-Weffc++",
app.cxxflags += "-Wmultiple-inheritance", "-Wvirtual-inheritance"
app.cxxflags += "-ffile-prefix-map=$srcdir/="

app.ldflags += "-flto"

app.src("src/main.cc")
