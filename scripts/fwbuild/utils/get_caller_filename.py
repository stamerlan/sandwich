import inspect
import pathlib

def get_caller_filename():
    """ Get a filename of caller of this function caller """
    frame = inspect.stack()[2]
    return pathlib.Path(frame[0].f_code.co_filename)
