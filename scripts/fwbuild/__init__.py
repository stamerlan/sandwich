import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

from fwbuild.include import include
import atexit
import fwbuild.build_config
import fwbuild.platforms
import pathlib

# Setup top source directory and top output directory
topdir = pathlib.Path(sys.modules["__main__"].__file__).parent
topout = pathlib.Path()

def set_topout(*args):
    global topout

    if hasattr(set_topout, "set"):
        return

    # Set topout only if build from source tree
    if topdir.samefile(pathlib.Path.cwd()):
        topout = pathlib.Path(*args)
    set_topout.set = True

# Set of files used during configuration. If any file in the list changed
# configure script has to be run again.
# Each path is either absolute or relative to fwbuild.topdir and starts with
# $topdir.
conf_files: set[pathlib.Path] = set()

def add_conf_file(filename: str | pathlib.Path):
    filename = pathlib.Path(filename)
    if filename.is_relative_to(topdir):
        filename = pathlib.Path("$topdir", filename.relative_to(topdir))
    conf_files.add(filename)

# Add this file and include.py to conf_files
add_conf_file(__file__)
add_conf_file(pathlib.Path(__file__).parent / "include.py")
add_conf_file(pathlib.Path(__file__).parent / "build_config.py")

# Configuration symbols loaded by fwbuild.kconfig()
conf = fwbuild.build_config.BuildConfig()

# Current platform
platform: fwbuild.platforms.base | None = None

def write_buildfiles(entry_point_filename: str):
    if all(sys.exc_info()):
        return
    if platform is not None:
        platform.write_buildfiles(entry_point_filename)
atexit.register(write_buildfiles, sys.modules["__main__"].__file__)
