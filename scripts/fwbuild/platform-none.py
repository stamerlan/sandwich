from types import ModuleType
import fwbuild
import importlib.util
import pathlib
import sys

def load(filename: str | pathlib.Path) -> ModuleType:
    filename = pathlib.Path(filename)
    mod_name = "fwbuild.platform." + filename.stem

    spec = importlib.util.spec_from_file_location(mod_name, filename.as_posix())
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    fwbuild.platform = mod
    spec.loader.exec_module(mod)
    return mod
