import pathlib

class files_set(object):
    """ Set of file paths.

        Stores file paths relative to topdir if possible.
    """

    def __init__(self, topdir: str | pathlib.Path, *filenames):
        self._topdir = pathlib.Path(topdir)
        self._files: set[pathlib.Path] = set()

        for f in filenames:
            self.add(f)

    @property
    def files(self) -> set[pathlib.Path]:
        return self._files

    def add(self, *path: pathlib.Path | str):
        fname = pathlib.Path(*path)
        if fname.is_relative_to(self._topdir):
            fname = pathlib.Path("$topdir", fname.relative_to(self._topdir))
        self._files.add(fname)
