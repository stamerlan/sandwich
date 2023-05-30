#!/usr/bin/env python3
import argparse
import scripts.fwbuild as fwbuild

# Parse command line
parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

# Load configuration
fwbuild.kconfig(args.config)

# Load platform-specific code
fwbuild.include("platform")

# Setup output directory
fwbuild.set_topout("bin", fwbuild.platform.name)

# Add sources
fwbuild.include("src/build.py")
