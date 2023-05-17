from .target_base import target_base
import fwbuild
import fwbuild.utils
import pathlib

class cxx(target_base):
    """ An executable compiled by C++ compiler """

    def __init__(self, name: str, srcdir: pathlib.Path | str):
        self._name: str = name

        self._asflags  = fwbuild.utils.str_list()
        self._cxxflags = fwbuild.utils.str_list()
        self._ldflags  = fwbuild.utils.str_list()
        self._ldlibs   = fwbuild.utils.str_list()
        self._ldscript: fwbuild.utils.src_path | None = None
        self._src: list[fwbuild.utils.src_path] = []

        self._gen_binary = False
        self._gen_dasm = False
        self._gen_map = False

        self._srcdir = pathlib.Path(srcdir)

        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        fwbuild.add_conf_file(__file__)

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
    def gen_binary(self) -> bool:
        return self._gen_binary

    @gen_binary.setter
    def gen_binary(self, value: bool):
        self._gen_binary = bool(value)

    @property
    def gen_dasm(self) -> bool:
        return self._gen_dasm

    @gen_dasm.setter
    def gen_dasm(self, value: bool):
        self._gen_dasm = bool(value)

    @property
    def gen_map(self) -> bool:
        return self._gen_map

    @gen_map.setter
    def gen_map(self, value: bool):
        self._gen_map = bool(value)

    @property
    def ldflags(self) -> fwbuild.utils.str_list:
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        if value is None:
            self._ldflags = None
        self._ldflags = fwbuild.utils.str_list(value)

    @property
    def ldlibs(self) -> fwbuild.utils.str_list:
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        self._ldlibs = fwbuild.utils.str_list(value)

    @property
    def ldscript(self) -> fwbuild.utils.src_path | None:
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = fwbuild.utils.src_path(value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def sources(self) -> list[fwbuild.utils.src_path]:
        return self._src

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
