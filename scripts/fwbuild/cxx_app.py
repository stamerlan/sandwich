from .caller import caller
from .cxx_module import cxx_module
from .kconfig import kconfig
from .node import node
from .str_list import str_list

class cxx_app(cxx_module):
    """ Base class for C++ application targets """

    def __init__(self, conf: kconfig, toolchain, name: str | None = None):
        """ TODO: toolchain type annotation """
        if name is None:
            name = self.__class__.__name__
        super().__init__(self, name, caller().dir)

        self._ldflags = str_list()
        self._ldlibs  = str_list()
        self._ldscript: node | None = None

        self.binary = False
        self.disassembly = False
        self.mapfile = False

        self.default = True

    @property
    def ldflags(self) -> str_list:
        return self._ldflags

    @ldflags.setter
    def ldflags(self, value):
        self._ldflags = str_list(value)

    @property
    def ldlibs(self) -> str_list:
        return self._ldlibs

    @ldlibs.setter
    def ldlibs(self, value):
        self._ldlibs = str_list(value)

    @property
    def ldscript(self) -> node | None:
        return self._ldscript

    @ldscript.setter
    def ldscript(self, value):
        if value is None:
            self._ldscript = None
        else:
            self._ldscript = node(value)
