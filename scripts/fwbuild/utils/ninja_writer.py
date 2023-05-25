import fwbuild
import fwbuild.utils
import pathlib
import shlex
import sys

def to_shell(cmdline: str):
    if sys.platform == "win32":
        return f'cmd /c "{cmdline}"'
    else:
        return cmdline

class ninja_writer(object):
    """ ninja_syntax.Write wrapper.

    Context manager which returns ninja_sytax.Write object. Adds commands to
    call configure script if any file in fwbuild.conf_files has been changed.
    """

    def __init__(self, filename: str | pathlib.Path,
                 config_out_files: None | str | pathlib.Path | list[None | str | pathlib.Path] = None,
                 width=78):
        self.filename = filename
        self.width = width

        self.file = None
        self.writer = None

        filename = pathlib.Path(filename)
        if filename.is_relative_to(fwbuild.topout):
            filename = filename.relative_to(fwbuild.topout)
        self.build_file = filename.as_posix()

        self._config_out_files: set[str] = set()
        if not isinstance(config_out_files, list):
            config_out_files = [config_out_files]
        for fname in config_out_files:
            if fname is None:
                continue
            fname = pathlib.Path(fname)
            if fname.is_relative_to(fwbuild.topout):
                fname = fname.relative_to(fwbuild.topout)
            self._config_out_files.add(fname.as_posix())

    def __enter__(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.filename, "w")
        self.writer = fwbuild.utils.ninja_syntax.Writer(self.file, self.width)
        return self.writer

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.writer.newline()
        self.writer.comment("Regenerate build file if build script changed")
        self.writer.rule("configure",
            command=fwbuild.utils.shell_cmd().cd(pathlib.Path.cwd()).cmd(sys.executable, sys.argv),
            generator=True,
            description="CONFIGURE")
        self.writer.build(self.build_file, "configure",
            implicit_outputs=sorted(self._config_out_files),
            implicit=sorted(fwbuild.conf_files))

        self.file.close()
