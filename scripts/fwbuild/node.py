import pathlib

_WELL_KNOWN_DIRS = ("$outdir", "$srcdir", "$topdir")

class node(object):
    """ Represents a single file path.

        The file path may have additional metadata. For example metadata may
        contain additional cflags to compile the C source file.
    """

    def __init__(self, path: str | pathlib.Path, **meta):
        path = pathlib.Path(path)
        if len(path.parts) == 0 or path.is_absolute() or path.parts[0] in _WELL_KNOWN_DIRS:
            self._path = path
        elif path.parts[0] == "topout":
            self._path = pathlib.Path(*path.parts[1:])
        else:
            self._path = pathlib.Path("$srcdir", path)

        self._meta = {**meta}

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def meta(self) -> dict:
        return self._meta

    def __str__(self) -> str:
        return self._path.as_posix()
