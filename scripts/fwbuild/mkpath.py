from pathlib import Path

path_t = str | Path

def mkpath(p: path_t, default: path_t, **dirs) -> Path:
    """ Make path relative to topdir/topout/srcdir/outdir"""
    p = Path(p)
    if (len(p.parts) != 0 and
            not p.is_absolute() and
            p.parts[0] not in ("$topdir", "$topout", "$srcdir", "$topout")):
        p = Path(default, p)

    if len(p.parts):
        for name, value in dirs.items():
            if p.parts[0] == "$" + name:
                p = Path(value, *p.parts[1:])
                break

    return p

def relative_path(p: path_t, **dirs) -> Path:
    p = Path(p)
    for name, value in dirs.items():
        value_path = Path(value)
        if p.is_relative_to(value_path):
            return Path("$" + name, p.relative_to(value_path))
    return p
