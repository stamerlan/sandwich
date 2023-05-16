import pathlib

class src_path(object):
    """ Source file path """

    def __init__(self, path: str | pathlib.Path, **vars):
        self._path = pathlib.Path(path)
        if (self._path.parts[0] not in ("$outdir", "$srcdir") and
           not self._path.is_absolute()):
            self._path = pathlib.Path("$srcdir") / self._path

        self._vars = {**vars}

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def vars(self) -> dict[str, str]:
        return self._vars

    def __str__(self) -> str:
        return self._path.as_posix()
