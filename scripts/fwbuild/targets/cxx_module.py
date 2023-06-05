from .target_base import target_base
from typing import Optional, Type, Union
import fwbuild
import fwbuild.utils
import pathlib

fwbuild.deps.add(__file__)

class cxx_module(target_base):
    def __init__(self, name: Optional[str] = None,
                 target = None, srcdir: Optional[pathlib.Path | str] = None):
        super().__init__()

        if name is None:
            name = fwbuild.utils.caller().stem
        self._name = name

        if srcdir is None:
            srcdir = fwbuild.utils.caller().dir
        srcdir = pathlib.Path(srcdir)
        if srcdir.is_relative_to(fwbuild.topdir):
            srcdir = pathlib.Path("$topdir", srcdir.relative_to(fwbuild.topdir))
        self._srcdir = srcdir

        self._asflags  = fwbuild.utils.str_list()
        self._cxxflags = fwbuild.utils.str_list()
        self._includes: list[fwbuild.utils.src_path] = []
        self._src: list[fwbuild.utils.src_path] = []

        self._target = target
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
    def includes(self) -> list[fwbuild.utils.src_path]:
        return self._includes

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

    def include(self, *include_dirs):
        """ Add directories to C prerprocessor search path """
        for d in include_dirs:
            self._includes.append(fwbuild.utils.src_path(d))

    def src(self, *sources, **vars):
        """ Add source file/files to compile list """
        for filename in sources:
            self._src.append(fwbuild.utils.src_path(filename, **vars))

    def submodule(self, submodule: Union["cxx_module", Type["cxx_module"], str, pathlib.Path],
                  *args, **kwargs) -> "cxx_module":
        if isinstance(submodule, type) and issubclass(submodule, cxx_module):
            submodule = submodule(target=self._target, *args, **kwargs)
        elif not isinstance(submodule, cxx_module):
            mod_path = pathlib.Path(submodule)
            if not mod_path.is_absolute():
                mod_path = fwbuild.utils.caller().dir / mod_path
            mod = fwbuild.include(mod_path)
            cls = getattr(mod, mod_path.stem, None)
            if cls is None:
                raise RuntimeError(f'"{mod.__file__}" has no module class "{submodule.stem}"')
            if isinstance(cls, cxx_module):
                raise RuntimeError(f'Unexpected module class type {cls} defined at "{mod.__file__}"')
            submodule = cls(target=self._target, *args, **kwargs)

        self._submodules.append(submodule)
        return self._submodules
