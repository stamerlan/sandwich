import fwbuild
import pathlib

class src_path(object):
    """ Source file path """

    def __init__(self, path: str | pathlib.Path, **vars):
        path = pathlib.Path(path)
        if (len(path.parts) == 0):
            self._path = pathlib.Path(".")
        elif (path.parts[0] in ("$outdir", "$srcdir", "$topdir") or
                path.is_absolute()):
            self._path = path
        elif path.parts[0] == "$topout":
            self._path = pathlib.Path(*path.parts[1:])
        else:
            self._path = pathlib.Path("$srcdir", path)
        self._vars = {**vars}

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def vars(self) -> dict[str, str]:
        return self._vars

    def __str__(self) -> str:
        return self._path.as_posix()
