from .cxx_module import cxx_module
from typing import Any
import fwbuild
import fwbuild.utils
import itertools
import pathlib

fwbuild.deps.add(__file__)

class cxx_app(cxx_module):
    """ An executable compiled by C++ compiler """

    def __init__(self, name: str, toolchain: Any, srcdir: pathlib.Path | str):
        super().__init__(name, self, srcdir)

        self._ldflags  = fwbuild.utils.str_list()
        self._ldlibs   = fwbuild.utils.str_list()
        self._ldscript: fwbuild.utils.src_path | None = None

        self._gen_binary = False
        self._gen_dasm = False
        self._gen_map = False

        self._toolchain = toolchain

    def __str__(self) -> str:
        lines = []
        lines.append(f"{self.name} {type(self)} at {self.srcdir}")
        lines.append(f"  gen_binary: {self.gen_binary}")
        lines.append(f"  gen_dasm:   {self.gen_dasm}")
        lines.append(f"  gen_map:    {self.gen_map}")
        lines.append("")
        lines.append(f"  ldflags:    {self.ldflags}")
        lines.append(f"  ldlibs:     {self.ldlibs}")
        if self.ldscript:
            lines.append(f"  ldscript:   {self.ldscript}")

        return "\n".join(itertools.chain(lines, super().__str__().split("\n")[1:]))

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
    def toolchain(self):
        return self._toolchain

    def write_buildfile(self, writer: fwbuild.utils.ninja_syntax.Writer,
                        outdir: str | pathlib.Path = pathlib.Path()):
        self.toolchain.write_buildfile(writer, self, outdir)
