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

    def __init__(self, filename, width=78):
        self.filename = filename
        self.width = width

        self.file = None
        self.writer = None

        filename = pathlib.Path(filename)
        if filename.is_relative_to(fwbuild.outdir):
            filename = filename.relative_to(fwbuild.outdir)
        self.build_file = filename.as_posix()

    def __enter__(self):
        self.file = open(self.filename, "w")
        self.writer = fwbuild.utils.ninja_syntax.Writer(self.file, self.width)
        return self.writer

    def __exit__(self, exc_type, exc_value, exc_traceback):
        cmd = ' '.join(map(shlex.quote, sys.argv))

        self.writer.newline()
        self.writer.comment("Regenerate build file if build script changed")
        self.writer.rule("configure",
            command=to_shell(f"cd \"{pathlib.Path.cwd()}\" && {sys.executable} {cmd}"),
            generator=True,
            description="CONFIGURE")
        self.writer.build(self.build_file, "configure",
            implicit=sorted(fwbuild.conf_files),
            variables={"topsrcdir": fwbuild.srcdir.as_posix()})

        self.file.close()
