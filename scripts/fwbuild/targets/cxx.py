import fwbuild
import fwbuild.utils
import pathlib

class cxx(object):
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
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._asflags

    @asflags.setter
    def asflags(self, value):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        self._asflags = fwbuild.utils.str_list(value)

    @property
    def cxxflags(self) -> fwbuild.utils.str_list:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._cxxflags

    @cxxflags.setter
    def cxxflags(self, value):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        self._cxxflags = fwbuild.utils.str_list(value)

    @property
    def gen_binary(self) -> bool:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._gen_binary

    @gen_binary.setter
    def gen_binary(self, value: bool):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        self._gen_binary = bool(value)

    @property
    def gen_dasm(self) -> bool:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._gen_dasm

    @gen_dasm.setter
    def gen_dasm(self, value: bool):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        self._gen_dasm = bool(value)

    @property
    def gen_map(self) -> bool:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._gen_map

    @gen_map.setter
    def gen_map(self, value: bool):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        self._gen_map = bool(value)

    @property
    def ldflags(self) -> fwbuild.utils.str_list:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        if value is None:
            self._ldflags = None
        self._ldflags = fwbuild.utils.str_list(value)

    @property
    def ldlibs(self) -> fwbuild.utils.str_list:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        self._ldlibs = fwbuild.utils.str_list(value)

    @property
    def ldscript(self) -> fwbuild.utils.src_path | None:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = fwbuild.utils.src_path(value)

    @property
    def name(self) -> str:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._name

    @property
    def sources(self) -> list[fwbuild.utils.src_path]:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._src

    @property
    def srcdir(self) -> str:
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return self._srcdir.as_posix()

    def src(self, sources, **vars):
        """ Add source file/files to compile list """
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        if isinstance(sources, (str, pathlib.Path)):
            self._src.append(fwbuild.utils.src_path(sources, **vars))
        else:
            for filename in sources:
                self._src.append(fwbuild.utils.src_path(filename, **vars))

