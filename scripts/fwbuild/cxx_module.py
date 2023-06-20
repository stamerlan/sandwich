from pathlib import Path
import fwbuild

class cxx_module(object):
    """ Base class for C++ modules.

    C++ module is a set of files which usually are stored at the same directory
    and have some common set of flags. Modules also can have submodules. Module
    is compiled-in to target image.
    """

    def __init__(self, target: "fwbuild.cxx_app", name: str | None = None,
                 srcdir: str | Path | None = None):
        """ Construct C++ module

        target: target object the module compiled-in.
        name: module name. If name is none it's set to caller's filename.
        srcdir: module sources directory. If none it's set to caller's dirname.
        """
        if name is None:
            if fwbuild.caller().cls is not None:
                name = fwbuild.caller().cls.__name__
            else:
                name = fwbuild.caller().stem

        self._name = name

        if srcdir is None:
            srcdir = fwbuild.caller().dir
        self._srcdir = Path(srcdir)

        self._asflags  = fwbuild.str_list()
        self._cxxflags = fwbuild.str_list()
        self._defines  = fwbuild.str_list()
        self._includes: list[Path] = []
        self._src:      list[fwbuild.node] = []

        self._target = target
        self._submodules: list["cxx_module"] = []

    def __str__(self) -> str:
        return f"{self._name}@{self._srcdir.as_posix()}"

    @property
    def asflags(self) -> "fwbuild.str_list":
        return self._asflags

    @asflags.setter
    def asflags(self, value):
        self._asflags = fwbuild.str_list(value)

    @property
    def cxxflags(self) -> "fwbuild.str_list":
        return self._cxxflags

    @cxxflags.setter
    def cxxflags(self, value):
        self._cxxflags = fwbuild.str_list(value)

    @property
    def defines(self) -> "fwbuild.str_list":
        return self._defines

    @defines.setter
    def defines(self, value):
        self._defines = fwbuild.str_list(value)

    @property
    def includes(self) -> list[Path]:
        return self._includes

    @property
    def name(self) -> str:
        return self._name

    @property
    def sources(self) -> list["fwbuild.node"]:
        return self._src

    @property
    def srcdir(self) -> Path:
        return self._srcdir

    @property
    def submodules(self) -> list["cxx_module"]:
        return self._submodules

    @property
    def target(self) -> "fwbuild.cxx_app":
        return self._target

    def include(self, dir: str | Path):
        """ Add a directory to C preprocessor search path """
        dir = fwbuild.mkpath(dir, default=fwbuild.caller().dir)
        self._includes.append(dir)

    def src(self, *sources, **vars):
        """ Add source files to sources list """
        for s in sources:
            src = fwbuild.mkpath(s, default=fwbuild.caller().dir)
            self._src.append(fwbuild.node(src, **vars))

    def submodule(self, name: str) -> "cxx_module":
        for cls in fwbuild.module_cls:
            if cls.__name__ == name:
                mod = cls(self.target)
                self._submodules.append(mod)
                return mod
        raise RuntimeError(f'Submodule "{name}" not found')
