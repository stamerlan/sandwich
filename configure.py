#!/usr/bin/env python3
import argparse
import scripts.fwbuild as fwbuild

parser = argparse.ArgumentParser(description="Sandwich configuration script")
parser.add_argument("--platform", choices=["raspi3b", "host"],
                    default="host", help="Target platform")
conf = parser.parse_args()

fwbuild.platform.load(f"platform/{conf.platform}/platform.py")
if str(fwbuild.topout) != ".":
    fwbuild.topout /= conf.platform

import src.build

