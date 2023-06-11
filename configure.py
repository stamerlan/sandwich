#!/usr/bin/env python3
import argparse
import scripts.fwbuild as fwbuild

# Parse command line
parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

# Load configuration
print(fwbuild.conf.load_kconfig(args.config))

# Load platform-specific code
if fwbuild.conf.PLATFORM_HOST:
    fwbuild.platform = fwbuild.include("platforms/host").host()
elif fwbuild.conf.PLATFORM_RASPI3B:
    fwbuild.platform = fwbuild.include("platforms/raspi3b").Raspi3bPlatform()

# Setup output directory
fwbuild.set_topout("bin", fwbuild.platform.name)

# Add sources
fwbuild.include("src/build.py")

fwbuild.platform.write_buildfiles(__file__)
