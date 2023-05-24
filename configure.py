#!/usr/bin/env python3
import argparse
import kconfiglib
import menuconfig
import os
import scripts.fwbuild as fwbuild

parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("-c", "--config", "--cfg", "--conf",
    help="Filename to load configuration from")
args = parser.parse_args()

os.environ["srctree"] = str(fwbuild.topdir)
kconf = kconfiglib.Kconfig(fwbuild.topdir / "Kconfig")
if args.config is None:
    args.config = ".config"
    menuconfig.menuconfig(kconf)
else:
    kconf.load_config(args.config)

if kconf.syms["PLATFORM_HOST"].tri_value:
    platform_name = "host"
elif kconf.syms["PLATFORM_RASPI3B"].tri_value:
    platform_name = "raspi3b"

fwbuild.platform.load(f"platform/{platform_name}/{platform_name}.py")
if str(fwbuild.topout) != ".":
    fwbuild.topout /= platform_name

import src.build
