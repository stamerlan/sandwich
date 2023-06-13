import contextlib
import os
import pathlib
import sys

class tool(object):
    """ Represent an executable found on build PC """

    @staticmethod
    def find_all(prog: str, *search_dirs: str | pathlib.Path,
                 name: str | None = None):
        dirs = os.getenv("PATH")
        if dirs is None:
            try:
                dirs = os.confstr("CS_PATH")
            except (ArithmeticError, ValueError):
                dirs = os.defpath
        if dirs is None:
            dirs = []
        else:
            dirs = dirs.split(os.pathsep)

        for d in search_dirs:
            dirs.append(d)

        for d in dirs:
            with contextlib.suppress(FileNotFoundError):
                yield tool(d, prog, name=name)

    @staticmethod
    def find(prog: str, *search_dirs: str | pathlib.Path,
             name: str | None = None):
        with contextlib.suppress(StopIteration):
            return next(tool.find_all(prog, *search_dirs, name=name))
        raise FileNotFoundError(f'Tool "{prog}" is not found')

    def __init__(self, *path_parts, name: str | None = None):
        fname = pathlib.Path(*path_parts)

        if name is None:
            name = fname.stem
        self._name = name

        if sys.platform != "win32" or fname.suffix:
            files = [fname]
        else:
            # CMD defaults in Windows 10
            WIN_DEFAULT_PATHEXT = ".COM;.EXE;.BAT;.CMD;.VBS;.JS;.WS;.MSC"
            ext = os.getenv("PATHEXT") or WIN_DEFAULT_PATHEXT
            ext = [e.lower() for e in ext.split(os.pathsep) if e]

            files = [fname] + [fname.with_suffix(e) for e in ext]

        for f in files:
            if f.is_file() and os.access(f, os.X_OK):
                self._path = f
                break
        else:
            raise FileNotFoundError(fname.as_posix())

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> pathlib.Path:
        return self._path

    def __str__(self) -> str:
        return self._path.as_posix()
