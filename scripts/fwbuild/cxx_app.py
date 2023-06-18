from .cxx_module import cxx_module
from pathlib import Path
import fwbuild

class cxx_app(cxx_module):
    """ Base class for C++ application targets """

    class artifacts(object):
        """ Artifacts produced by building cxx_app """

        def __init__(self):
            self.app : Path | None = None
            self.objs: list[Path]  = []
            self.bin : Path | None = None
            self.dasm: Path | None = None
            self.map : Path | None = None


    def __init__(self, conf: "fwbuild.kconfig", toolchain: "fwbuild.toolchain",
                 name: str | None = None, srcdir: str | Path | None = None):
        if name is None:
            name = self.__class__.__name__
        super().__init__(self, name, srcdir or fwbuild.caller().dir)

        self.conf = conf
        self.toolchain = toolchain

        self._ldflags = fwbuild.str_list()
        self._ldlibs  = fwbuild.str_list()
        self._ldscript: Path | None = None

        self.binary      = False
        self.disassembly = False
        self.mapfile     = False

        self.default = True

    @property
    def ldflags(self) -> "fwbuild.str_list":
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        self._ldflags = fwbuild.str_list(value)

    @property
    def ldlibs(self) -> "fwbuild.str_list":
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        self._ldlibs = fwbuild.str_list(value)

    @property
    def ldscript(self) -> Path | None:
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = fwbuild.mkpath(value, default=fwbuild.caller().dir)
