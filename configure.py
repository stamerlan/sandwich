#!/usr/bin/env python3
import scripts.fwbuild as fwbuild
import argparse

# Parse command line
parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

# Load configuration
conf = fwbuild.kconfig(fwbuild.topdir)
print(conf.load_config(args.config))

#class hello(fwbuild.cxx_app):
#    def __init__(self, conf, toolchain):
#        super().__init__(conf, toolchain)
#m = hello(None, None)
m = fwbuild.cxx_app(None, None)
print(m)
m.cxxflags += '-Wall', "-Wextra"
print(f"  cxxflags: {m.cxxflags}")
m.src("src/main.cc", cxxflags="-Os")
for s in m.sources:
    print(f"{s.path.as_posix()} {s.meta}")

#@fwbuild.target
#class hello(fwbuild.cxx_app):
#    def init(self, conf, toolchain):
#        super().init(conf, toolchain)
#        self.src("main.cc")

#if conf.PLATFORM_HOST:
#    build = fwbuild.ninja(PlatformHost(conf), "bin/host/ninja.build")
#elif conf.PLATFORM_RASPI3B:
#    build = fwbuild.ninja(PlatformRaspi3b(conf), "bin/raspi3b/ninja.build")
#else:
#    raise RuntimeError("Unknown platform")
#fwbuild.vscode(build, ".vscode/")
