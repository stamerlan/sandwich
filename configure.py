#!/usr/bin/env python3
import scripts.fwbuild as fwbuild

fwbuild.platform.load(fwbuild.srcdir / "platform/raspi3b/platform.py")

fw = fwbuild.platform.cxx_target("hello")
fw.cxxflags += "-std=c++23", "-g", "-O3"
fw.cxxflags += "-fcheck-new", "-flto", "-fno-rtti", "-fno-exceptions"
fw.cxxflags += "-fno-threadsafe-statics"
fw.cxxflags += "-Wall", "-Wextra", "-Werror", "-Weffc++",
fw.cxxflags += "-Wmultiple-inheritance", "-Wvirtual-inheritance"
fw.cxxflags += "-ffile-prefix-map=$srcdir/="

fw.src("src/main.cc")
