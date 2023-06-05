import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

from fwbuild.include import include
import atexit
import fwbuild.build_config
import fwbuild.config_deps
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

deps = fwbuild.config_deps.ConfigDeps(topdir,
    __file__,
    pathlib.Path(__file__).parent / "build_config.py",
    pathlib.Path(__file__).parent / "config_deps.py",
    pathlib.Path(__file__).parent / "include.py",
)

# Configuration symbols loaded by fwbuild.kconfig()
conf = fwbuild.build_config.BuildConfig(topdir)

# Current platform
platform = None

def write_buildfiles(entry_point_filename: str):
    if all(sys.exc_info()):
        return
    if platform is not None:
        platform.write_buildfiles(entry_point_filename)
atexit.register(write_buildfiles, sys.modules["__main__"].__file__)
