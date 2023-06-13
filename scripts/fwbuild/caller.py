import inspect
import pathlib

class caller(object):
    def __init__(self, frame_nr = 1):
        frame_info = inspect.stack()[frame_nr + 1]
        self._filename = pathlib.Path(frame_info.filename)
        self._lineno = frame_info.lineno

    @property
    def filename(self) -> pathlib.Path:
        return self._filename

    @property
    def name(self) -> str:
        return self._filename.name

    @property
    def stem(self) -> str:
        return self._filename.stem

    @property
    def dir(self) -> pathlib.Path:
        return self._filename.parent

    @property
    def lineno(self) -> int:
        return self._lineno
