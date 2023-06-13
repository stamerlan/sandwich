from .caller import caller
from .cxx_module import cxx_module

class cxx_app(cxx_module):
    """ Base class for C++ application targets """

    def __init__(self, conf, toolchain, name: str | None = None):
        if name is None:
            name = self.__class__.__name__
        print("cxx_app:", name)
        super().__init__(self, name, caller().dir)
