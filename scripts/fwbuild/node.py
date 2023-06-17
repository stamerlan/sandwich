import pathlib

class node(object):
    """ Represents a single file path.

        The file path may have additional metadata. For example metadata may
        contain additional cflags to compile the C source file.
    """

    def __init__(self, path: str | pathlib.Path, **vars):
        self._path = pathlib.Path(path)
        self._vars = {**vars}

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def vars(self) -> dict:
        return self._vars

    def __str__(self) -> str:
        return self._path.as_posix()
