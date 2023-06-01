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
#fwbuild.include("platform")
if fwbuild.conf.PLATFORM_HOST:
    import platforms.host
    fwbuild.platform = platforms.host.HostPlatform()
elif fwbuild.conf.PLATFORM_RASPI3B:
    import platforms.raspi3b
    fwbuild.platform = platforms.raspi3b.Raspi3bPlatform()

# Setup output directory
fwbuild.set_topout("bin", fwbuild.platform.name)

# Add sources
import src.build
