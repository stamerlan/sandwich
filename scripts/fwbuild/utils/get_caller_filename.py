import inspect
import pathlib

def get_caller_filename(frame_nr = 1) -> pathlib.Path:
    return pathlib.Path(inspect.stack()[frame_nr + 1][0].f_code.co_filename)
