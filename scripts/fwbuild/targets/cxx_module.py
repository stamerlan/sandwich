from .target_base import target_base
from typing import Optional
import fwbuild.utils
import pathlib

class cxx_module(target_base):
    def __init__(self, name: Optional[str] = None,
                 srcdir: Optional[pathlib.Path | str] = None):
        super().__init__()
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())

        if name is None:
            name = fwbuild.utils.get_caller_filename().stem
        self._name = name
        if srcdir is None:
            srcdir = fwbuild.utils.get_caller_filename().parent
        self._srcdir = pathlib.Path(srcdir)

        self._asflags  = fwbuild.utils.str_list()
        self._cxxflags = fwbuild.utils.str_list()
        self._src: list[fwbuild.utils.src_path] = []

        self._submodules: list["cxx_module"] = []

    def __str__(self) -> str:
        lines = []
        lines.append(f'Module "{self.name}" at {self.srcdir}')
        lines.append(f"  asflags:    {self.asflags}")
        lines.append(f"  cxxflags:   {self.cxxflags}")
        lines.append(f"  Sources:")
        for s in self.sources:
            lines.append(f"    {s}")
            for key, value in s.vars.items():
                lines.append(f"      {key}: {value}")
        for submodule in self.submodules:
            for l in str(submodule).split("\n"):
                lines.append("  " + l)
        return "\n".join(lines)

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
    def submodules(self) -> list["cxx_module"]:
        return self._submodules

    @property
    def name(self) -> str:
        return self._name

    @property
    def sources(self) -> list[fwbuild.utils.src_path]:
        return self._src

    @property
    def srcdir(self) -> str:
        return self._srcdir.as_posix()

    def src(self, *sources, **vars):
        """ Add source file/files to compile list """
        for filename in sources:
            self._src.append(fwbuild.utils.src_path(filename, **vars))

    def submodule(self, submodule: "cxx_module"):
        self._submodules.append(submodule)
