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

        self._build_files: set[str] = set()
        this_file = pathlib.Path(__file__)
        try:
            this_file = \
                pathlib.Path("$srcdir", this_file.relative_to(self._srcdir))
        except ValueError:
            pass
        self._build_files.add(this_file.as_posix())
        self._add_caller_to_build_files()

    @property
    def asflags(self) -> fwbuild.utils.str_list:
        self._add_caller_to_build_files()
        return self._asflags

    @asflags.setter
    def asflags(self, value):
        self._add_caller_to_build_files()
        self._asflags = fwbuild.utils.str_list(value)

    @property
    def build_files(self) -> list[str]:
        self._add_caller_to_build_files()
        return sorted(self._build_files)

    @property
    def cxxflags(self) -> fwbuild.utils.str_list:
        self._add_caller_to_build_files()
        return self._cxxflags

    @cxxflags.setter
    def cxxflags(self, value):
        self._add_caller_to_build_files()
        self._cxxflags = fwbuild.utils.str_list(value)

    @property
    def gen_binary(self) -> bool:
        self._add_caller_to_build_files()
        return self._gen_binary

    @gen_binary.setter
    def gen_binary(self, value: bool):
        self._add_caller_to_build_files()
        self._gen_binary = bool(value)

    @property
    def gen_dasm(self) -> bool:
        self._add_caller_to_build_files()
        return self._gen_dasm

    @gen_dasm.setter
    def gen_dasm(self, value: bool):
        self._add_caller_to_build_files()
        self._gen_dasm = bool(value)

    @property
    def gen_map(self) -> bool:
        self._add_caller_to_build_files()
        return self._gen_map

    @gen_map.setter
    def gen_map(self, value: bool):
        self._add_caller_to_build_files()
        self._gen_map = bool(value)

    @property
    def ldflags(self) -> fwbuild.utils.str_list:
        self._add_caller_to_build_files()
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        self._add_caller_to_build_files()
        if value is None:
            self._ldflags = None
        self._ldflags = fwbuild.utils.str_list(value)

    @property
    def ldlibs(self) -> fwbuild.utils.str_list:
        self._add_caller_to_build_files()
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        self._add_caller_to_build_files()
        self._ldlibs = fwbuild.utils.str_list(value)

    @property
    def ldscript(self) -> fwbuild.utils.src_path | None:
        self._add_caller_to_build_files()
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        self._add_caller_to_build_files()
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = fwbuild.utils.src_path(value)

    @property
    def name(self) -> str:
        self._add_caller_to_build_files()
        return self._name

    @property
    def sources(self) -> list[fwbuild.utils.src_path]:
        self._add_caller_to_build_files()
        return self._src

    @property
    def srcdir(self) -> str:
        self._add_caller_to_build_files()
        return self._srcdir.as_posix()

    def src(self, sources, **vars):
        """ Add source file/files to compile list """
        self._add_caller_to_build_files()
        if isinstance(sources, (str, pathlib.Path)):
            self._src.append(fwbuild.utils.src_path(sources, **vars))
        else:
            for filename in sources:
                self._src.append(fwbuild.utils.src_path(filename, **vars))

    def _add_caller_to_build_files(self):
        """ Add caller's caller file to set of files which define the target """
        fname = fwbuild.utils.get_caller_filename(2)
        try:
            fname = pathlib.Path("$srcdir", fname.relative_to(self._srcdir))
        except ValueError:
            pass
        self._build_files.add(fname.as_posix())
