from .tool import tool
from argparse import Namespace

class toolchain(object):
    """ Base class for toolchain implementation """

    def __init__(self, name: str):
        self.name = name
        self.tools = Namespace()
