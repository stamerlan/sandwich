import fwbuild
import inspect
import pathlib

class caller(object):
    def __init__(self, frame_nr = 1):
        """ This object constructr's caller """
        self._path = pathlib.Path(
            inspect.stack()[frame_nr + 1][0].f_code.co_filename)

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(self._path)

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def stem(self) -> str:
        return self._path.stem

    @property
    def dir(self) -> pathlib.Path:
        return self._path.parent
