from types import ModuleType
from typing import Optional
import fwbuild
import pathlib
import sys
import importlib.abc
import importlib.util

_module_fullname: str = None
_module: Optional[ModuleType] = None

class PlatformFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        global _module_fullname

        if not fullname.startswith("fwbuild.platform."):
            return

        if _module_fullname:
            raise ImportError(
                f"Can't load platform '{fullname}' because another platform '{_module_fullname}' already loaded")

        mod_path = pathlib.Path(*fullname.split(".")[1:])

        file_paths = [
            fwbuild.topdir / mod_path.with_suffix(".py"),
            fwbuild.topdir / mod_path / "__init__.py",
            fwbuild.topdir / mod_path / mod_path.with_suffix(".py").name,
        ]
        for filename in file_paths:
            if filename.is_file():
                spec = importlib.util.spec_from_file_location(fullname, filename)
                _module_fullname = fullname
                return spec

def __getattr__(name: str):
    global _module
    global _module_fullname

    if _module is None:
        if _module_fullname:
            _module = sys.modules[_module_fullname]
        else:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    return getattr(_module, name)

sys.meta_path.append(PlatformFinder())
