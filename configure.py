#!/usr/bin/env python3
import scripts.fwbuild as fwbuild
import argparse
import fwbuild.platforms
import platforms

import drivers.build
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

# Load platform
if conf.PLATFORM_HOST:
    target_platform = fwbuild.platforms.host(conf)
elif conf.PLATFORM_RASPI3B:
    target_platform = platforms.raspi3b(conf)
else:
    raise RuntimeError("Unknown platform")

# Write build files
builddir = f"bin/{target_platform.name}"
conf.write_autoconf(f"{builddir}/config.h")
artifacts = fwbuild.ninja(target_platform, f"{builddir}/build.ninja")

#fwbuild.vscode(artifacts, ".vscode/")
