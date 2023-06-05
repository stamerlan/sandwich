import fwbuild
import fwbuild.utils
import pathlib

fwbuild.deps.add(__file__)

class ninja_writer(object):
    """ ninja_syntax.Write wrapper """

    def __init__(self, filename: str | pathlib.Path,
                 width=78):
        self.filename = filename
        self.width = width

        self.file = None
        self.writer = None

        filename = pathlib.Path(filename)
        if filename.is_relative_to(fwbuild.topout):
            filename = filename.relative_to(fwbuild.topout)
        self.build_file = filename.as_posix()

    def __enter__(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.filename, "w")
        self.writer = fwbuild.utils.ninja_syntax.Writer(self.file, self.width)
        return self.writer

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()
