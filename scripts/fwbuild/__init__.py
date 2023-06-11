import sys

# Make the package available by name 'fwbuild'
if __name__ != "fwbuild":
    sys.modules["fwbuild"] = sys.modules[__name__]

from fwbuild.include import include
import inspect
import fwbuild.build_config
import fwbuild.config_deps
import fwbuild.platforms
import pathlib

# Setup top source directory and top output directory
topdir = pathlib.Path(sys.modules["__main__"].__file__).parent
topout = pathlib.Path()
this_dir: pathlib.Path
root = pathlib.Path(__file__).parent

def set_topout(*args):
    global topout

    if hasattr(set_topout, "set"):
        return

    # Set topout only if build from source tree
    if topdir.samefile(pathlib.Path.cwd()):
        topout = pathlib.Path(*args)
    set_topout.set = True

deps = fwbuild.config_deps.config_deps(topdir)

# Configuration symbols loaded by fwbuild.kconfig()
conf = fwbuild.build_config.build_config(topdir)

# Current platform
platform: fwbuild.platforms.base = None

def __getattr__(name):
    if name == 'this_dir':
        return pathlib.Path(inspect.stack()[1][0].f_code.co_filename).parent
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
