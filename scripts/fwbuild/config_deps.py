import contextlib
import os
import pathlib
import sys

class config_deps(object):
    def __init__(self, topdir: pathlib.Path | str, *deps):
        self.topdir = pathlib.Path(topdir)
        self._files: set[pathlib.Path] = set()

        fwbuild_dir = pathlib.Path(sys.modules["fwbuild"].__file__).parent
        for root, dirs, files in os.walk(fwbuild_dir, followlinks=True):
            for name in files:
                self.add(root, name)
            with contextlib.suppress(ValueError):
                dirs.remove("__pycache__")

        for d in deps:
            self.add(d)

    @property
    def files(self) -> set[pathlib.Path]:
        return self._files

    def add(self, *args: pathlib.Path | str):
        filename = pathlib.Path(*args)
        if filename.is_relative_to(self.topdir):
            filename = pathlib.Path("$topdir", filename.relative_to(self.topdir))
        self._files.add(filename)
