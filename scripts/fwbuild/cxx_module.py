from .caller import caller
from .mkpath import mkpath
from .node import node
from .str_list import str_list
import pathlib

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cxx_app import cxx_app

class cxx_module(object):
    """ Base class for C++ modules.

    C++ module is a set of files which usually are stored at the same directory
    and have some common set of flags. Modules also can have submodules. Module
    is compiled-in to target image.

    TODO: Add method to add a submodule
    """

    def __init__(self, target: "cxx_app", name: str | None = None,
                 srcdir: str | pathlib.Path | None = None):
        """ Construct C++ module

        target: target object the module compiled-in.
        name: module name. If name is none it's set to caller's filename.
        srcdir: module sources directory. If none it's set to caller's dirname.
        """
        if name is None:
            name = caller().stem
        self._name = name

        if srcdir is None:
            srcdir = caller().dir
        self._srcdir = pathlib.Path(srcdir)

        self._asflags  = str_list()
        self._cxxflags = str_list()
        self._defines  = str_list()
        self._includes: list[pathlib.Path] = []
        self._src:      list[node] = []

        self._target = target
        self._submodules: list["cxx_module"] = []

    def __str__(self) -> str:
        return f"{self._name}@{self._srcdir.as_posix()}"

    @property
    def asflags(self) -> str_list:
        return self._asflags

    @asflags.setter
    def asflags(self, value):
        self._asflags = str_list(value)

    @property
    def cxxflags(self) -> str_list:
        return self._cxxflags

    @cxxflags.setter
    def cxxflags(self, value):
        self._cxxflags = str_list(value)

    @property
    def defines(self) -> str_list:
        return self._defines

    @defines.setter
    def defines(self, value):
        self._defines = str_list(value)

    @property
    def includes(self) -> list[pathlib.Path]:
        return self._includes

    @property
    def name(self) -> str:
        return self._name

    @property
    def sources(self) -> list[node]:
        return self._src

    @property
    def srcdir(self) -> pathlib.Path:
        return self._srcdir

    @property
    def submodules(self) -> list["cxx_module"]:
        return self._submodules

    @property
    def target(self) -> "cxx_app":
        return self._target

    def include(self, dir: str | pathlib.Path):
        """ Add a directory to C preprocessor search path """
        dir = mkpath(dir, default=caller().dir)
        self._includes.append(dir)

    def src(self, *sources, **vars):
        """ Add source files to sources list """
        for s in sources:
            self._src.append(node(mkpath(s, default=caller().dir), **vars))
