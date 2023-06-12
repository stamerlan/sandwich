#!/usr/bin/env python3
import scripts.fwbuild as fwbuild

import argparse
import drivers
import platforms.host
import platforms.raspi3b
import src.build

# Parse command line
parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

conf = fwbuild.kconfig(args.config)
if fwbuild.conf.PLATFORM_HOST:
    build = fwbuild.ninja(PlatformHost(conf), "bin/host/ninja.build")
elif fwbuild.conf.PLATFORM_RASPI3B:
    build = fwbuild.ninja(PlatformRaspi3b(conf), "bin/raspi3b/ninja.build")
fwbuild.vscode(build, ".vscode/")
