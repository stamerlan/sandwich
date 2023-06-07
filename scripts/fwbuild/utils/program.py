import os
import pathlib
import sys

class program(object):
    """ Represent an executable found on build PC """

    def __init__(self, *path_parts):
        fname = pathlib.Path(*path_parts)

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
                self._filename = f
                break
        else:
            raise FileNotFoundError(f'Program "{fname.as_posix()}" is not found')

    @property
    def path(self) -> pathlib.Path:
        return self._filename

    def __str__(self) -> str:
        return self._filename.as_posix()
