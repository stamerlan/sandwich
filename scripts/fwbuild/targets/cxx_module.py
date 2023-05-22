from .target_base import target_base
from typing import Optional
import fwbuild.utils
import pathlib

class cxx_module(target_base):
    def __init__(self, name: str, parent: "cxx_module",
                 srcdir: pathlib.Path | str):
        super().__init__()
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())

        self._name = name
        self._parent = parent
        self._srcdir = pathlib.Path(srcdir)

        self._asflags  = fwbuild.utils.str_list()
        self._cxxflags = fwbuild.utils.str_list()
        self._src: list[fwbuild.utils.src_path] = []

        self._modules: list["cxx_module"] = []

    @property
    def asflags(self) -> fwbuild.utils.str_list:
        return self._asflags

    @asflags.setter
    def asflags(self, value):
        self._asflags = fwbuild.utils.str_list(value)

    @property
    def cxxflags(self) -> fwbuild.utils.str_list:
        return self._cxxflags

    @cxxflags.setter
    def cxxflags(self, value):
        self._cxxflags = fwbuild.utils.str_list(value)

    @property
    def modules(self) -> list["cxx_module"]:
        return self._modules

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> Optional["cxx_module"]:
        return self._parent

    @property
    def srcdir(self) -> str:
        return self._srcdir.as_posix()

    def src(self, sources, **vars):
        """ Add source file/files to compile list """
        if isinstance(sources, (str, pathlib.Path)):
            self._src.append(fwbuild.utils.src_path(sources, **vars))
        else:
            for filename in sources:
                self._src.append(fwbuild.utils.src_path(filename, **vars))

    def submodule(self, name: str, srcdir: pathlib.Path | str) -> "cxx_module":
        submod = cxx_module(name, self, srcdir)
        self._modules.append(submod)
        return submod
