#!/usr/bin/env python3
import scripts.fwbuild as fwbuild
import argparse

import drivers.build
import platforms.host
import sandwich.build
import src.build

# Parse command line
parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

# Load configuration
conf = fwbuild.kconfig(fwbuild.topdir)
print(conf.load_config(args.config))
fwbuild.deps |= conf.deps

# Write build files
if conf.PLATFORM_HOST:
    build = fwbuild.ninja(platforms.host.host(conf), "bin/host/build.ninja")
#elif conf.PLATFORM_RASPI3B:
#    build = fwbuild.ninja(PlatformRaspi3b(conf), "bin/raspi3b/build.ninja")
else:
    raise RuntimeError("Unknown platform")

#fwbuild.vscode(build, ".vscode/")
