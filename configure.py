#!/usr/bin/env python3
import scripts.fwbuild as fwbuild
import fwbuild.toolchains
import platforms.host
import argparse

# Parse command line
parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

# Load configuration
conf = fwbuild.kconfig(fwbuild.topdir)
print(conf.load_config(args.config))

def print_cxx_app(app: fwbuild.cxx_app):
    print(app)
    print(f"  cxxflags: {app.cxxflags}")
    print(f"  includes: {[str(i) for i in app.includes]}")
    for s in app.sources:
        print(f"  {s.path.as_posix()}", end='')
        if s.meta:
            print(f" {s.meta}", end='')
        print()

def print_toolchain(toolchain: fwbuild.toolchain):
    print(f"{toolchain.name}@{toolchain.tools.cc.path.parent.as_posix()}")
    for name, tool in toolchain.tools.items():
        print(f"  {name}: {tool}")

@fwbuild.target
class hello(fwbuild.cxx_app):
    def __init__(self, conf, toolchain):
        super().__init__(conf, toolchain)

        self.cxxflags += "-Wall", "-Wextra"
        self.include("drivers/uart/include")

        self.src("src/main.cc", cxxflags="-Os")
        self.src("drivers/uart/src/host.cc")

@fwbuild.target
class test(fwbuild.cxx_gtest):
    pass

host = platforms.host.host(conf)

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
