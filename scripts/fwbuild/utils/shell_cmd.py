from typing import Optional
import itertools
import pathlib
import shlex
import sys

def _escape(s: str) -> str:
    if sys.platform == "win32":
        if '"' in s:
            s = s.replace('"', '\\"')
        if ' ' in s:
            s = f'"{s}"'
    else:
        s = shlex.quote(s)
    return s

class shell_cmd(object):
    """ Shell command builder """

    def __init__(self, *args, **kwargs):
        self._commands: list[str] = []
        self._call_shell: bool = False
        if args or kwargs:
            self.cmd(*args, **kwargs)

    def cd(self, work_dir: str | pathlib.Path) -> "shell_cmd":
        work_dir = pathlib.Path(work_dir)
        self._commands.append("cd " + _escape(work_dir.as_posix()))
        return self

    def cmd(self, exec: str | pathlib.Path, args: list[str] = [],
            stdout: Optional[str | pathlib.Path] = None) -> "shell_cmd":
        exec = pathlib.Path(exec).as_posix()
        cmd = ' '.join(map(_escape, itertools.chain([exec], args)))
        if stdout is not None:
            stdout = pathlib.Path(stdout)
            cmd += " > " + _escape(stdout.as_posix())
            self._call_shell = True
        self._commands.append(cmd)
        self._call_shell = self._call_shell or (len(self._commands) > 1)
        return self

    def __str__(self) -> str:
        if sys.platform == "win32":
            if not self._call_shell:
                return self._commands[0]
            return "cmd /S /C " + " && ".join(self._commands)
        else:
            return " && ".join(self._commands)
