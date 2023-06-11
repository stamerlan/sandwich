import contextlib
import os
import pathlib
import sys

class config_deps(object):
    def __init__(self, topdir: pathlib.Path | str, *deps: pathlib.Path | str):
        self.topdir = pathlib.Path(topdir)
        self._files: set[pathlib.Path] = set()

        # Add fwbuild package files
        fwbuild_dir = pathlib.Path(sys.modules["fwbuild"].__file__).parent
        for root, dirs, files in os.walk(fwbuild_dir, followlinks=True):
            for name in files:
                self.add(root, name)
            with contextlib.suppress(ValueError):
                dirs.remove("__pycache__")

        # Add configuration script
        self.add(sys.modules["__main__"].__file__)

        # Add additional dependencies
        for d in deps:
            self.add(d)

    @property
    def files(self) -> set[pathlib.Path]:
        return self._files

    def add(self, *args: pathlib.Path | str):
        fname = pathlib.Path(*args)
        if fname.is_relative_to(self.topdir):
            fname = pathlib.Path("$topdir", fname.relative_to(self.topdir))
        self._files.add(fname)
