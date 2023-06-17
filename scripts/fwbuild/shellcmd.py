from itertools import chain
from pathlib import Path
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

class shellcmd(object):
    """ Class to construct shell command line """

    def __init__(self, *args, **kwargs):
        self._commands: list[str] = []
        self._call_shell: bool = False
        if args or kwargs:
            self.cmd(*args, **kwargs)

    def cd(self, dir: str | Path) -> "shellcmd":
        dir = Path(dir)
        self._commands.append("cd " + _escape(dir.as_posix()))
        return self

    def cmd(self, exec: str | Path, *args: str,
            stdout: str | Path | None = None) -> "shellcmd":
        exec = str(Path(exec))
        cmd = ' '.join(map(_escape, chain([exec], [*args])))
        if stdout is not None:
            stdout = Path(stdout)
            cmd += " > " + _escape(str(Path(stdout)))
            self._call_shell = True
        self._commands.append(cmd)
        self._call_shell = self._call_shell or (len(self._commands) > 1)
        return self

    def __str__(self) -> str:
        if sys.platform == "win32":
            if self._call_shell:
                return "cmd /S /C " + " && ".join(self._commands)
            else:
                return self._commands[0]
        else:
            return " && ".join(self._commands)
