from typing import Any
from .tool import tool

class tools_ns(object):
    def __init__(self):
        self._tools: dict[str, tool] = {}

    def __getitem__(self, name: str) -> tool:
        return self._tools[name]

    def __setitem__(self, name: str, value: Any):
        if not isinstance(value, tool):
            value = tool(value, name=name)

        self._tools[name] = value
        self.__dict__[name] = value

    def __delitem__(self, name: str):
        del self._tools[name]
        del self.__dict__[name]

    def __setattr__(self, name: str, value: Any):
        if name == "_tools":
            self.__dict__["_tools"] = value
            return

        if not isinstance(value, tool):
            value = tool(value)

        self._tools[name] = value
        self.__dict__[name] = value

    def __delattr__(self, name: str):
        del self._tools[name]
        del self.__dict__[name]


class toolchain(object):
    """ Base class for toolchain implementation """

    def __init__(self, name: str):
        self.name = name
        self.tools = tools_ns()
