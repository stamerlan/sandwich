import pathlib

class ConfigDeps(object):
    def __init__(self, topdir: pathlib.Path | str, *deps):
        self.topdir = pathlib.Path(topdir)
        print(f"ConfigDeps@{self.topdir.as_posix()}")
        self._files: set[pathlib.Path] = set()

        for d in deps:
            self.add(d)

    @property
    def files(self) -> set[pathlib.Path]:
        return self._files

    def add(self, filename: pathlib.Path | str):
        filename = pathlib.Path(filename)
        if filename.is_relative_to(self.topdir):
            filename = pathlib.Path("$topdir", filename.relative_to(self.topdir))
        self._files.add(filename)
