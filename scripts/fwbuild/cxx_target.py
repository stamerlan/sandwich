import inspect
import pathlib
import sys
from .str_list import str_list

class source_file(object):
    def __init__(self, filename, **vars):
        self._filename = pathlib.Path(filename)
        if (self._filename.parts[0] not in ("$outdir", "$srcdir") and
           not self._filename.is_absolute()):
            self._filename = pathlib.Path("$srcdir") / self._filename

        self._vars = {**vars}

    @property
    def filename(self) -> pathlib.Path:
        return self._filename

    @property
    def vars(self) -> dict[str, str]:
        return self._vars

    def __str__(self) -> str:
        return self._filename.as_posix()


class cxx_target(object):
    def __init__(self, name: str, srcdir: pathlib.Path | str | None = None):
        self._name: str = name

        self._asflags = str_list()
        self._cxxflags = str_list()
        self._ldflags = str_list()
        self._ldlibs = str_list()
        self._ldscript: source_file | None = None
        self._src: list[source_file] = []

        self._gen_binary = False
        self._gen_dasm = False
        self._gen_map = False

        if srcdir is not None:
            self._srcdir = pathlib.Path(srcdir)
        else:
            frame = inspect.stack()[1]
            caller_file = frame[0].f_code.co_filename
            self._srcdir = pathlib.Path(caller_file).parent

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
    def ldflags(self) -> str_list:
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        if value is None:
            self._ldflags = None
        self._ldflags = str_list(value)

    @property
    def ldlibs(self) -> str_list:
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        self._ldlibs = str_list(value)

    @property
    def ldscript(self) -> source_file | None:
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = source_file(value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def sources(self) -> list[source_file]:
        return self._src

    @property
    def srcdir(self) -> str:
        return self._srcdir.as_posix()

    def src(self, sources, **vars):
        if isinstance(sources, (str, pathlib.Path)):
            self._src.append(source_file(sources, **vars))
        else:
            for filename in sources:
                self._src.append(source_file(sources, **vars))
