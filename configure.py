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

if conf.PLATFORM_HOST:
    build = fwbuild.ninja(PlatformHost(conf), "bin/host/ninja.build")
elif conf.PLATFORM_RASPI3B:
    build = fwbuild.ninja(PlatformRaspi3b(conf), "bin/raspi3b/ninja.build")
else:
    raise RuntimeError("Unknown platform")
fwbuild.vscode(build, ".vscode/")
