#!/usr/bin/env python3
import argparse
import scripts.fwbuild as fwbuild

parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

fwbuild.kconfig(args.config)

if fwbuild.conf.PLATFORM_HOST:
    platform_name = "host"
elif fwbuild.conf.PLATFORM_RASPI3B:
    platform_name = "raspi3b"

fwbuild.platform.load(f"platform/{platform_name}/{platform_name}.py")
if str(fwbuild.topout) != ".":
    fwbuild.topout /= platform_name

import src.build
