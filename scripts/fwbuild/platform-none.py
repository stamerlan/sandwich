from types import ModuleType
import fwbuild
import fwbuild.utils
import pathlib
import sys

def load(filename: str | pathlib.Path) -> ModuleType:
    filename = pathlib.Path(filename)
    if not filename.is_absolute():
        filename = fwbuild.utils.get_caller_filename().parent / filename

    mod_name = "fwbuild.platform." + filename.stem

    mod = fwbuild.include(filename, mod_name)
    sys.modules[mod_name] = mod
    fwbuild.platform = mod
    return mod
