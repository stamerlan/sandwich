import pathlib
import fwbuild.utils

class cxx_target(object):
    """ An executable compiled by C++ compiler """

    def __init__(self, name: str, srcdir: pathlib.Path | str | None = None):
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

        self._regen_on: set[str] = set([__file__])
        self._add_regen_dep()

        if srcdir is not None:
            self._srcdir = pathlib.Path(srcdir)
        else:
            self._srcdir = fwbuild.utils.get_caller_filename().parent

    @property
    def asflags(self) -> fwbuild.utils.str_list:
        self._add_regen_dep()
        return self._asflags

    @asflags.setter
    def asflags(self, value):
        self._add_regen_dep()
        self._asflags = fwbuild.utils.str_list(value)

    @property
    def cxxflags(self) -> fwbuild.utils.str_list:
        self._add_regen_dep()
        return self._cxxflags

    @cxxflags.setter
    def cxxflags(self, value):
        self._add_regen_dep()
        self._cxxflags = fwbuild.utils.str_list(value)

    @property
    def gen_binary(self) -> bool:
        self._add_regen_dep()
        return self._gen_binary

    @gen_binary.setter
    def gen_binary(self, value: bool):
        self._add_regen_dep()
        self._gen_binary = bool(value)

    @property
    def gen_dasm(self) -> bool:
        self._add_regen_dep()
        return self._gen_dasm

    @gen_dasm.setter
    def gen_dasm(self, value: bool):
        self._add_regen_dep()
        self._gen_dasm = bool(value)

    @property
    def gen_map(self) -> bool:
        self._add_regen_dep()
        return self._gen_map

    @gen_map.setter
    def gen_map(self, value: bool):
        self._add_regen_dep()
        self._gen_map = bool(value)

    @property
    def ldflags(self) -> fwbuild.utils.str_list:
        self._add_regen_dep()
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        self._add_regen_dep()
        if value is None:
            self._ldflags = None
        self._ldflags = fwbuild.utils.str_list(value)

    @property
    def ldlibs(self) -> fwbuild.utils.str_list:
        self._add_regen_dep()
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        self._add_regen_dep()
        self._ldlibs = fwbuild.utils.str_list(value)

    @property
    def ldscript(self) -> fwbuild.utils.src_path | None:
        self._add_regen_dep()
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        self._add_regen_dep()
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = fwbuild.utils.src_path(value)

    @property
    def name(self) -> str:
        self._add_regen_dep()
        return self._name

    @property
    def regen_on(self) -> list[str]:
        self._add_regen_dep()
        return [x.replace(str(self._srcdir), "$srcdir") for x in sorted(list(self._regen_on))]

    @property
    def sources(self) -> list[fwbuild.utils.src_path]:
        self._add_regen_dep()
        return self._src

    @property
    def srcdir(self) -> str:
        self._add_regen_dep()
        return self._srcdir.as_posix()

    def src(self, sources, **vars):
        """ Add source file/files to compile list """
        self._add_regen_dep()
        if isinstance(sources, (str, pathlib.Path)):
            self._src.append(fwbuild.utils.src_path(sources, **vars))
        else:
            for filename in sources:
                self._src.append(fwbuild.utils.src_path(filename, **vars))

    def _add_regen_dep(self):
        """ Add a file which called parent function to list of dependencies.
        It used to build a list target dependencies. If any python file which
        accessed the target has been changed then build file should be
        regenerated.
        """
        self._regen_on.add(fwbuild.utils.get_caller_filename().as_posix())
