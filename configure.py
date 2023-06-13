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
app = hello(None, None)

class gcc(fwbuild.toolchain):
    def __init__(self, prefix: str = "", *search_dirs):
        super().__init__(prefix + "gcc")
        self._prefix = prefix

        for cc in fwbuild.tool.find_all("gcc", search_dirs, name="cc"):
            try:
                self.tools.cc = cc

                dir = cc.path.parent
                tools = {
                    "ar":  prefix + "ar",
                    "cxx": prefix + "g++",
                    "ld":  prefix + "ld",
                    "objcopy": prefix + "objcopy",
                    "objdump": prefix + "objdump",
                }

                for name, prog in tools.items():
                    self.tools[name] = fwbuild.tool(dir, prog, name=name)
                break
            except FileNotFoundError:
                continue
        else:
            raise FileNotFoundError(f'Toolchain "{prefix}gcc" not found')


class host_platform(object):
    def __init__(self, conf: fwbuild.kconfig):
        self._toolchain = gcc()
        self._targets = []
        for cls in fwbuild.targets:
            if issubclass(cls, fwbuild.cxx_app):
                self._targets.append(cls(conf, self._toolchain))
            else:
                raise RuntimeError(f"Unexpected target {cls}")

        print_toolchain(self._toolchain)
        for target in self._targets:
            print_cxx_app(target)

host = host_platform(conf)

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
